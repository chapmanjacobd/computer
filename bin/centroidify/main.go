package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"runtime"
	"sync"
	"time"

	"github.com/alecthomas/kong"
	"github.com/twpayne/go-geos"
)

// CLI defines the command-line arguments and flags.
type CLI struct {
	Input  string `arg:"" help:"Input GeoJSONL file." default:"grouped_by_wikipedia.geojsonl" type:"path"`
	Output string `arg:"" help:"Output GeoJSONL file." default:"wikipedia_pois.geojsonl" type:"path"`
}

// rawFeature preserves every key in the source JSON untouched.
type rawFeature map[string]json.RawMessage

// Job represents a single line of input JSON to be processed.
type Job struct {
	LineNum int64
	Raw     []byte
}

// Result represents the processed geometry or metadata for writing.
type Result struct {
	LineNum       int64
	OutBytes      []byte
	SkippedNoGeom bool
	SkippedErr    bool
}

func main() {
	var cli CLI
	kong.Parse(&cli,
		kong.Name("centroidify"),
		kong.Description("Reads grouped_by_wikipedia.geojsonl and writes wikipedia_pois.geojsonl with every geometry replaced by a Point."),
		kong.UsageOnError(),
	)

	in, err := os.Open(cli.Input)
	if err != nil {
		log.Fatalf("open input: %v", err)
	}

	out, err := os.Create(cli.Output)
	if err != nil {
		_ = in.Close() // Best effort close before fatal
		log.Fatalf("create output: %v", err)
	}

	// 2 MiB write buffer — important for a 6 GB+ output file.
	bw := bufio.NewWriterSize(out, 2<<20)

	// 128 MiB line buffer — safe for large multipolygon geometries.
	scanner := bufio.NewScanner(in)
	scanner.Buffer(make([]byte, 1<<16), 128<<20)

	var (
		total, written, skippedNoGeom, skippedErr int64
		start                                     = time.Now()
	)

	numWorkers := runtime.NumCPU()
	jobs := make(chan Job, numWorkers*2)
	results := make(chan Result, numWorkers*2)

	var wg sync.WaitGroup
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go worker(jobs, results, &wg)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	// Output writer goroutine
	writerDone := make(chan struct{})
	go func() {
		defer close(writerDone)
		buffer := make(map[int64]Result)
		var nextLineNum int64 = 1

		for res := range results {
			buffer[res.LineNum] = res

			for {
				bufferedRes, ok := buffer[nextLineNum]
				if !ok {
					break // waiting for nextLineNum to arrive
				}
				delete(buffer, nextLineNum)

				if bufferedRes.SkippedNoGeom {
					skippedNoGeom++
				} else if bufferedRes.SkippedErr {
					skippedErr++
				} else {
					if _, err := bw.Write(bufferedRes.OutBytes); err != nil {
						log.Fatalf("write failed: %v", err)
					}
					if err := bw.WriteByte('\n'); err != nil {
						log.Fatalf("write byte failed: %v", err)
					}
					written++
				}

				if nextLineNum%50_000 == 0 {
					elapsed := time.Since(start).Round(time.Second)
					fmt.Fprintf(os.Stderr, "  %d processed, %d written (%v elapsed)\n",
						nextLineNum, written, elapsed)
				}
				nextLineNum++
			}
		}
	}()

	for scanner.Scan() {
		raw := scanner.Bytes()
		if len(raw) == 0 {
			continue
		}
		total++

		// make a copy of the line to send to the worker
		rawCopy := make([]byte, len(raw))
		copy(rawCopy, raw)

		jobs <- Job{
			LineNum: total,
			Raw:     rawCopy,
		}
	}

	if err := scanner.Err(); err != nil {
		log.Fatalf("scanner error: %v", err)
	}

	close(jobs)
	<-writerDone

	if err := bw.Flush(); err != nil {
		log.Fatalf("flush output: %v", err)
	}
	if err := out.Close(); err != nil {
		log.Fatalf("close output: %v", err)
	}
	if err := in.Close(); err != nil {
		log.Fatalf("close input: %v", err)
	}

	elapsed := time.Since(start).Round(time.Millisecond)
	fmt.Fprintf(os.Stderr,
		"\nDone in %v\n  total lines : %d\n  written     : %d\n  no geometry : %d\n  errors      : %d\n",
		elapsed, total, written, skippedNoGeom, skippedErr)
}

func worker(jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	ctx := geos.NewContext() // each worker gets its own GEOS context

	for job := range jobs {
		res := Result{LineNum: job.LineNum}

		var rf rawFeature
		if err := json.Unmarshal(job.Raw, &rf); err != nil {
			log.Printf("line %d: JSON parse error, skipping: %v", job.LineNum, err)
			res.SkippedErr = true
			results <- res
			continue
		}

		geomRaw, hasGeom := rf["geometry"]
		if !hasGeom || isNullJSON(geomRaw) {
			res.SkippedNoGeom = true
			results <- res
			continue
		}

		// Parse geometry — NewGeomFromGeoJSON does return (geom, error).
		g, err := ctx.NewGeomFromGeoJSON(string(geomRaw))
		if err != nil {
			log.Printf("line %d: invalid geometry, skipping: %v", job.LineNum, err)
			res.SkippedErr = true
			results <- res
			continue
		}

		// Pick the representative point (panics recovered inside).
		pt, isPoint, err := representativePoint(g, job.LineNum)
		if err != nil {
			log.Printf("line %d: %v, skipping", job.LineNum, err)
			res.SkippedErr = true
			results <- res
			continue
		}

		if isPoint {
			res.OutBytes = job.Raw
		} else {
			// ToGeoJSON returns a single string (no error).
			ptJSON := pt.ToGeoJSON(0) // 0 = no indent
			rf["geometry"] = json.RawMessage(ptJSON)
			outBytes, err := json.Marshal(rf)
			if err != nil {
				log.Printf("line %d: marshal failed, skipping: %v", job.LineNum, err)
				res.SkippedErr = true
				results <- res
				continue
			}
			res.OutBytes = outBytes
		}

		results <- res
	}
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
func representativePoint(g *geos.Geom, lineNum int64) (*geos.Geom, bool, error) {
	switch g.TypeID() {

	case geos.TypeIDPoint:
		return g, true, nil

	case geos.TypeIDLineString:
		pt, err := safeGeom(func() *geos.Geom {
			return g.InterpolateNormalized(0.5)
		})
		return pt, false, err

	case geos.TypeIDMultiLineString:
		pt, err := midpointOfLongestLine(g)
		if err != nil {
			log.Printf("line %d: MultiLineString midpoint failed (%v), falling back to PointOnSurface", lineNum, err)
			fallback, fbErr := safeGeom(func() *geos.Geom { return g.PointOnSurface() })
			return fallback, false, fbErr
		}
		return pt, false, nil

	case geos.TypeIDPolygon, geos.TypeIDMultiPolygon:
		centroid, err := safeGeom(func() *geos.Geom { return g.Centroid() })
		if err != nil {
			fallback, fbErr := safeGeom(func() *geos.Geom { return g.PointOnSurface() })
			return fallback, false, fbErr
		}
		intersects, err := safeBool(func() bool { return g.Intersects(centroid) })
		if err != nil || !intersects {
			fallback, fbErr := safeGeom(func() *geos.Geom { return g.PointOnSurface() })
			return fallback, false, fbErr
		}
		return centroid, false, nil

	default:
		// GeometryCollection, LinearRing, etc.
		fallback, fbErr := safeGeom(func() *geos.Geom { return g.PointOnSurface() })
		return fallback, false, fbErr
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
