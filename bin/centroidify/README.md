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
