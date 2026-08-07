#!/usr/bin/env python3
"""Buffer an arbitrary vector layer by N meters and clip it to the land layer.

The name says it all: the buffer of the input layer is cut off at the
land/water boundary (the land layer, e.g. a coastline or states file), so
only on-shore area is counted.

Generalizable: accepts any two vector layers (shp, zip, gpkg, ...) plus a
buffer distance in meters. Works in an equal-area projection (laea) centered
on the buffered layer, so distances are in meters and areas are meaningful
anywhere on Earth.

Usage:
    buffer.to.coastline.py LAND LAYER METERS [--target-pct P]

Examples:
    buffer.to.coastline.py tl_2025_us_state.zip tl_2025_us_uac20.zip 5000
    buffer.to.coastline.py tl_2025_us_state.zip tl_2025_us_uac20.zip 0

Arguments:
    LAND       vector layer defining the landmass (e.g. tl_2025_us_state.zip)
    LAYER      arbitrary layer to buffer (e.g. tl_2025_us_uac20.zip)
    METERS     buffer distance in meters (0 = the layer itself, clipped to land)

Options:
    --target-pct P    Instead of one buffer, binary-search the largest integer
                      buffer in meters whose land-clipped area stays under P% of
                      the US landmass.
    --us-land-km2 N   US landmass in km^2 for the "% of US landmass" column
                      (default 9147593, the Census land area of the 50 states + DC).
    --segments N      number of segments per quarter-circle for the buffer
                      (default 12; more = rounder but slower).
"""
import argparse
import sys
import warnings

try:
    from osgeo import ogr, osr
except ImportError:
    sys.exit("need osgeo (GDAL Python bindings): pip install GDAL")
try:
    from tabulate import tabulate
except ImportError:
    sys.exit("need tabulate: pip install tabulate")

warnings.filterwarnings("ignore")
ogr.UseExceptions()

DEFAULT_US_LAND_KM2 = 9_147_593


def open_layer(path):
    """Return (ds, layer). Keep ds alive for the layer's lifetime."""
    if path.lower().endswith(".zip"):
        import zipfile

        with zipfile.ZipFile(path) as z:
            shps = [n for n in z.namelist() if n.lower().endswith(".shp")]
        if len(shps) != 1:
            sys.exit(f"{path}: expected exactly one .shp inside the zip, found {len(shps)}")
        ds = ogr.Open(f"/vsizip/{path}/{shps[0]}")
    else:
        ds = ogr.Open(path)
    if ds is None:
        sys.exit(f"cannot open layer: {path}")
    return ds, ds.GetLayer()


def as_multipolygon(geoms):
    """Collect polygons/multipolygons into a single ogr MultiPolygon."""
    mp = ogr.Geometry(ogr.wkbMultiPolygon)
    for g in geoms:
        t = g.GetGeometryType()
        if t in (ogr.wkbPolygon, ogr.wkbPolygon25D):
            mp.AddGeometry(g)
        elif t in (ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D):
            for i in range(g.GetGeometryCount()):
                mp.AddGeometry(g.GetGeometryRef(i))
        else:
            sys.exit(f"unsupported geometry type {g.GetGeometryName()}")
    return mp


def union_all(geoms):
    """Union a list of polygons/multipolygons into one geometry."""
    return as_multipolygon(geoms).UnionCascaded()


def mean_center_wgs84(lyr, src):
    """Mean of feature centroids in WGS84 lon/lat (better than extent midpoint
    when the layer spans far-flung territories like the US + PR/Guam)."""
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(4326)
    wgs84.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    tx = osr.CoordinateTransformation(src, wgs84)
    sx = sy = n = 0.0
    for feat in lyr:
        g = feat.GetGeometryRef()
        if g is None or g.IsEmpty():
            continue
        c = g.Centroid()
        lon, lat, _ = tx.TransformPoint(c.GetX(), c.GetY())
        sx += lon
        sy += lat
        n += 1
    if n == 0:
        sys.exit("layer has no geometries")
    return sx / n, sy / n


def buffered_area(geoms, land, meters, quadsecs):
    """Return (raw_km2, clipped_km2) for the layer buffered by meters."""
    if meters == 0:
        combined = union_all(geoms)
    else:
        buffs = []
        for g in geoms:
            b = g.Buffer(meters, quadsecs)
            if not b.IsEmpty():
                buffs.append(b)
        combined = union_all(buffs)
    raw_km2 = combined.GetArea() / 1e6
    clipped_km2 = combined.Intersection(land).GetArea() / 1e6
    return raw_km2, clipped_km2


def solve(geoms, land, target_pct, us_land_km2, quadsecs):
    """Largest integer buffer (m) whose land-clipped area stays under target_pct."""
    def clipped_pct(m):
        _, km2 = buffered_area(geoms, land, m, quadsecs)
        return km2 / us_land_km2 * 100.0

    p0 = clipped_pct(0)
    if p0 >= target_pct:
        sys.exit(f"already {p0:.3f}% of US landmass at 0 m; target is {target_pct}%")
    hi = 1000.0
    while clipped_pct(hi) < target_pct:
        hi *= 10
        if hi > 1e7:
            sys.exit(f"target {target_pct}% not reached even at 10,000 km")
    lo = 0.0
    while hi - lo > 1:
        mid = (lo + hi) / 2
        if clipped_pct(mid) < target_pct:
            lo = mid
        else:
            hi = mid
    return lo, p0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("land", help="landmass layer (e.g. tl_2025_us_state.zip)")
    ap.add_argument("layer", help="arbitrary layer to buffer (e.g. tl_2025_us_uac20.zip)")
    ap.add_argument("meters", type=float, help="buffer distance in meters")
    ap.add_argument("--target-pct", type=float,
                    help="binary-search the max buffer keeping clipped area under P%%")
    ap.add_argument("--us-land-km2", type=float, default=DEFAULT_US_LAND_KM2,
                    help=f"US landmass in km^2 (default {DEFAULT_US_LAND_KM2:,})")
    ap.add_argument("--segments", type=int, default=12, metavar="N",
                    help="buffer segments per quarter-circle (default 12)")
    args = ap.parse_args()

    ds_land, land_lyr = open_layer(args.land)
    land_src = land_lyr.GetSpatialRef()
    if land_src is None:
        sys.exit(f"{args.land}: layer has no spatial reference")
    land_src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    ds, lyr = open_layer(args.layer)
    src = lyr.GetSpatialRef()
    if src is None:
        sys.exit(f"{args.layer}: layer has no spatial reference")
    src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    lon, lat = mean_center_wgs84(lyr, src)
    dst = osr.SpatialReference()
    dst.ImportFromProj4(f"+proj=laea +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs")
    dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    tx = osr.CoordinateTransformation(src, dst)

    geoms = []
    for feat in lyr:
        g = feat.GetGeometryRef()
        if g is None or g.IsEmpty():
            continue
        gg = g.Clone()
        gg.Transform(tx)
        geoms.append(gg)
    if not geoms:
        sys.exit(f"{args.layer}: no geometries to buffer")

    land_union = union_all(feat.GetGeometryRef().Clone()
                           for feat in land_lyr
                           if feat.GetGeometryRef() is not None
                           and not feat.GetGeometryRef().IsEmpty())
    land = land_union.Clone()
    land.Transform(tx)
    land_km2 = land.GetArea() / 1e6

    print(f"buffer: {args.meters:,.0f} m   US landmass: {args.us_land_km2:,.0f} km^2"
          f"   projection center: ({lon:.1f}, {lat:.1f})")
    print(f"land layer area (computed): {land_km2:,.0f} km^2\n")

    if args.target_pct is not None:
        best_m, p0 = solve(geoms, land, args.target_pct, args.us_land_km2, args.segments)
        raw, clip = buffered_area(geoms, land, best_m, args.segments)
        table = [
            ["layer @ 0 m (clipped)", f"{p0:.3f}%"],
            [f"max buffer @ {best_m:,.0f} m", f"{clip / args.us_land_km2 * 100:.3f}%"],
            ["raw buffer (unclipped) km^2", f"{raw:,.1f}"],
            ["clipped-to-land km^2", f"{clip:,.1f}"],
        ]
        print(tabulate(table, headers=["Measure", "Value"], tablefmt="grid"))
        print(f"\nlargest buffer under {args.target_pct}% of US landmass: {best_m:,.0f} m"
              f" ({best_m / 1000:,.2f} km)")
    else:
        raw, clip = buffered_area(geoms, land, args.meters, args.segments)
        table = [
            ["raw buffer (unclipped)", f"{raw:,.1f}", f"{raw / args.us_land_km2 * 100:.3f}%"],
            ["clipped to land", f"{clip:,.1f}", f"{clip / args.us_land_km2 * 100:.3f}%"],
        ]
        print(tabulate(table, headers=["Measure", "Area km^2", "% of US landmass"],
                       tablefmt="grid"))


if __name__ == "__main__":
    main()
