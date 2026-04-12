# centroidify

Converts every geometry in a GeoJSONL file to a single representative Point -- fast, in one pass, with no intermediate files.

| Geometry type | Strategy |
|---|---|
| Point | kept as-is |
| LineString | arc-length midpoint (`InterpolateNormalized(0.5)`) |
| MultiLineString | arc-length midpoint of the longest component |
| Polygon / MultiPolygon | centroid if it lies inside, else `PointOnSurface` |
| GeometryCollection / other | `PointOnSurface` fallback |

Features with null or missing geometry are dropped. All other properties pass through unchanged.

## Install

Requires GEOS and Go 1.22+.

```sh
# macOS
brew install geos

# Fedora
sudo dnf install geos-devel

# Ubuntu / Debian
sudo apt install libgeos-dev
```

```sh
go install github.com/chapmanjacobd/computer/bin/centroidify@latest
```

## Usage

```sh
centroidify input.geojsonl output.geojsonl
```

Progress is printed to stderr every 50k features.

## OSM planet.pbf to Wikipedia POIs

```sh
osmium tags-filter planet-260330.osm.pbf /wikipedia -o wikipedia_pois.osm.pbf
# (one hour)

osmium export wikipedia_pois.osm.pbf -f jsonseq  --format-option=print_record_separator=false | \
    jq -sc 'group_by(.properties.wikipedia) | map(max_by(.properties | length)) | sort_by(.properties | length) | reverse[]' \
    > grouped_by_wikipedia.geojsonl
# (six hours)
# .rw-r--r--@ 9.7G xk    9 Apr 16:09  grouped_by_wikipedia.geojsonl

rm -f wikipedia_pois.osm.pbf

centroidify grouped_by_wikipedia.geojsonl wikipedia.POIs.geojson
# (5 mins)
# .rw-r--r--@ 605M xk   11 Apr 20:12  wikipedia_pois.geojsonl
```
