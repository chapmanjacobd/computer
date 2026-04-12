// centroidify: reads grouped_by_wikipedia.geojsonl and writes
// final_wikipedia_pois.geojsonl with every geometry replaced by a Point.
//
// Strategy by geometry type:
//
//	Point                         → kept as-is
//	LineString                    → InterpolateNormalized(0.5)  (true arc-length midpoint)
//	MultiLineString               → InterpolateNormalized(0.5) on the longest component
//	Polygon / MultiPolygon        → Centroid if it intersects, else PointOnSurface
//	GeometryCollection / unknown  → PointOnSurface fallback
//
// Features with null/missing geometry are dropped.
//
// NOTE: go-geos methods do NOT return errors — they panic on bad input.
// All geometry calls are wrapped in safeGeom() which recovers panics and
// converts them to normal Go errors so one bad feature never kills the run.
//
// Dependencies (GEOS must be installed on the host):
//
//	Ubuntu/Debian: sudo apt install libgeos-dev
//	macOS:         brew install geos
//	go get github.com/twpayne/go-geos@latest
//
// Build:
//
//	go mod tidy && go build -o centroidify .
//
// Run:
//
//	./centroidify [input.geojsonl [output.geojsonl]]
//	(defaults: grouped_by_wikipedia.geojsonl → final_wikipedia_pois.geojsonl)
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/twpayne/go-geos"
)

// rawFeature preserves every key in the source JSON untouched.
type rawFeature map[string]json.RawMessage

func main() {
	inputPath := "grouped_by_wikipedia.geojsonl"
	outputPath := "final_wikipedia_pois.geojsonl"

	if len(os.Args) > 1 {
		inputPath = os.Args[1]
	}
	if len(os.Args) > 2 {
		outputPath = os.Args[2]
	}

	in, err := os.Open(inputPath)
	if err != nil {
		log.Fatalf("open input: %v", err)
	}
	defer in.Close()

	out, err := os.Create(outputPath)
	if err != nil {
		log.Fatalf("create output: %v", err)
	}
	defer out.Close()

	// 2 MiB write buffer — important for a 6 GB+ output file.
	bw := bufio.NewWriterSize(out, 2<<20)
	defer bw.Flush()

	ctx := geos.NewContext()

	// 128 MiB line buffer — safe for large multipolygon geometries.
	scanner := bufio.NewScanner(in)
	scanner.Buffer(make([]byte, 1<<16), 128<<20)

	var (
		total, written, skippedNoGeom, skippedErr int64
		start                                     = time.Now()
	)

	for scanner.Scan() {
		raw := scanner.Bytes()
		if len(raw) == 0 {
			continue
		}
		total++

		// Decode into a raw map so ALL keys survive unchanged.
		var rf rawFeature
		if err := json.Unmarshal(raw, &rf); err != nil {
			log.Printf("line %d: JSON parse error, skipping: %v", total, err)
			skippedErr++
			continue
		}

		geomRaw, hasGeom := rf["geometry"]
		if !hasGeom || isNullJSON(geomRaw) {
			skippedNoGeom++
			continue
		}

		// Parse geometry — NewGeomFromGeoJSON does return (geom, error).
		g, err := ctx.NewGeomFromGeoJSON(string(geomRaw))
		if err != nil {
			log.Printf("line %d: invalid geometry, skipping: %v", total, err)
			skippedErr++
			continue
		}

		// Pick the representative point (panics recovered inside).
		pt, err := representativePoint(g, total)
		if err != nil {
			log.Printf("line %d: %v, skipping", total, err)
			skippedErr++
			continue
		}

		// ToGeoJSON returns a single string (no error).
		ptJSON := pt.ToGeoJSON(0) // 0 = no indent

		rf["geometry"] = json.RawMessage(ptJSON)

		outBytes, err := json.Marshal(rf)
		if err != nil {
			log.Printf("line %d: marshal failed, skipping: %v", total, err)
			skippedErr++
			continue
		}

		bw.Write(outBytes)
		bw.WriteByte('\n')
		written++

		if total%50_000 == 0 {
			elapsed := time.Since(start).Round(time.Second)
			fmt.Fprintf(os.Stderr, "  %d processed, %d written (%v elapsed)\n",
				total, written, elapsed)
		}
	}

	if err := scanner.Err(); err != nil {
		log.Fatalf("scanner error: %v", err)
	}

	elapsed := time.Since(start).Round(time.Millisecond)
	fmt.Fprintf(os.Stderr,
		"\nDone in %v\n  total lines : %d\n  written     : %d\n  no geometry : %d\n  errors      : %d\n",
		elapsed, total, written, skippedNoGeom, skippedErr)
}

// ── helpers ────────────────────────────────────────────────────────────────────

func isNullJSON(b json.RawMessage) bool {
	return len(b) == 0 || string(b) == "null"
}

// safeGeom calls f() and converts any panic into an error.
// go-geos operations panic rather than returning errors.
func safeGeom(f func() *geos.Geom) (g *geos.Geom, err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("geos panic: %v", r)
		}
	}()
	return f(), nil
}

// safeBool calls a predicate and converts any panic into (false, error).
func safeBool(f func() bool) (result bool, err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("geos panic: %v", r)
		}
	}()
	return f(), nil
}

// representativePoint returns the best single Point for any geometry type.
func representativePoint(g *geos.Geom, lineNum int64) (*geos.Geom, error) {
	switch g.TypeID() {

	case geos.TypeIDPoint:
		return g, nil

	case geos.TypeIDLineString:
		return safeGeom(func() *geos.Geom {
			return g.InterpolateNormalized(0.5)
		})

	case geos.TypeIDMultiLineString:
		pt, err := midpointOfLongestLine(g)
		if err != nil {
			log.Printf("line %d: MultiLineString midpoint failed (%v), falling back to PointOnSurface", lineNum, err)
			return safeGeom(func() *geos.Geom { return g.PointOnSurface() })
		}
		return pt, nil

	case geos.TypeIDPolygon, geos.TypeIDMultiPolygon:
		centroid, err := safeGeom(func() *geos.Geom { return g.Centroid() })
		if err != nil {
			return safeGeom(func() *geos.Geom { return g.PointOnSurface() })
		}
		intersects, err := safeBool(func() bool { return g.Intersects(centroid) })
		if err != nil || !intersects {
			return safeGeom(func() *geos.Geom { return g.PointOnSurface() })
		}
		return centroid, nil

	default:
		// GeometryCollection, LinearRing, etc.
		return safeGeom(func() *geos.Geom { return g.PointOnSurface() })
	}
}

// midpointOfLongestLine finds the longest component of a MultiLineString
// and returns its arc-length midpoint via InterpolateNormalized(0.5).
func midpointOfLongestLine(multi *geos.Geom) (*geos.Geom, error) {
	n := multi.NumGeometries()
	if n == 0 {
		return nil, fmt.Errorf("empty MultiLineString")
	}

	var longest *geos.Geom
	var longestLen float64

	for i := range n {
		component := multi.Geometry(i)
		l := component.Length() // returns float64, no error
		if longest == nil || l > longestLen {
			longest = component
			longestLen = l
		}
	}

	return safeGeom(func() *geos.Geom {
		return longest.InterpolateNormalized(0.5)
	})
}
