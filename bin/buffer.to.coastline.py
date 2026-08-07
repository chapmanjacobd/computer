#!/usr/bin/env python3
"""Buffer an arbitrary vector layer by N meters and clip the result to land.

The "coastline" in the name: the buffer of the input layer is cut off at the
land/water boundary (the land layer, e.g. a coastline or states file), so only
on-shore area is counted. The buffered-and-clipped result is also saved next to
the input layer, named like the input with a random mktemp-style suffix
(e.g. tl_2025_us_uac20.A1B2C.zip).

To keep memory bounded on nationwide layers, the heavy geometry work (reproject,
simplify, buffer, clip, dissolve) is streamed feature-by-feature through the
native OGR tools (ogr2ogr with the SQLite dialect's GEOS functions), not held
as one giant in-memory geometry.

Usage:
    buffer.to.coastline.py LAND LAYER METERS [--target-pct P]

Examples:
    buffer.to.coastline.py tl_2025_us_state.zip tl_2025_us_uac20.zip 5000
    buffer.to.coastline.py tl_2025_us_state.zip tl_2025_us_uac20.zip 0 --target-pct 10

Arguments:
    LAND       vector layer defining the landmass (e.g. tl_2025_us_state.zip)
    LAYER      arbitrary layer to buffer (e.g. tl_2025_us_uac20.zip)
    METERS     buffer distance in meters (0 = the layer itself, clipped to land)

Options:
    --target-pct P    Instead of one buffer, binary-search the largest buffer in
                      meters whose land-clipped area stays under P% of the US
                      landmass.
    --simplify TOL    simplify the layer to TOL meters before buffering
                      (default 50; 0 disables). Speeds up the buffer enormously
                      with negligible area error (~0.03% on the 2020 urban areas).
    --format FMT      output format: zip, shp, fgb, gpkg
                      (default: same as LAYER's extension)
    --out-dir DIR     where to write the output (default: same folder as LAYER)
    --us-land-km2 N   US landmass in km^2 for the "% of US landmass" column
                      (default 9147593, the Census land area of the 50 states + DC).
"""
import argparse
import os
import random
import string
import subprocess
import sys
import tempfile
import warnings
import zipfile

warnings.filterwarnings("ignore")

try:
    from osgeo import ogr, osr
except ImportError:
    sys.exit("need osgeo (GDAL Python bindings): pip install GDAL")
try:
    from tabulate import tabulate
except ImportError:
    sys.exit("need tabulate: pip install tabulate")

ogr.UseExceptions()

DEFAULT_US_LAND_KM2 = 9_147_593


def open_layer(path):
    """Return (ds, layer) using the Python OGR bindings. Keep ds alive."""
    if path.lower().endswith(".zip"):
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


def layer_source_path(path):
    """Path that ogr2ogr can read directly (unzips nothing)."""
    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            shps = [n for n in z.namelist() if n.lower().endswith(".shp")]
        if len(shps) != 1:
            sys.exit(f"{path}: expected exactly one .shp inside the zip, found {len(shps)}")
        return f"/vsizip/{path}/{shps[0]}"
    return path


def layer_center_wgs84(path):
    """Mean of the layer's feature centroids in WGS84 lon/lat. Better than the
    extent midpoint when the layer spans far-flung territories."""
    ds, lyr = open_layer(path)
    src = lyr.GetSpatialRef()
    if src is None:
        sys.exit(f"{path}: layer has no spatial reference")
    src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
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
        sys.exit(f"{path}: layer has no geometries")
    return sx / n, sy / n, src.ExportToProj4()


def run(cmd, desc=None):
    if desc:
        print(f"  {desc}", file=sys.stderr)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{r.stderr}")


def mktemp_output_path(out_dir, base, ext):
    """Like mktemp --dry-run: base.XXXXX + ext, guaranteed not to exist."""
    for _ in range(100):
        token = "".join(random.choices(string.ascii_uppercase, k=5))
        p = os.path.join(out_dir, f"{base}.{token}{ext}")
        if not os.path.exists(p):
            return p
    sys.exit("could not allocate a free output name")


def package(clip_path, out_dir, base, fmt, src_proj4, tmpdir):
    """Transform the clipped layer back to the source CRS and write it as the
    final output in the requested format."""
    final_src = os.path.join(tmpdir, "final_src.shp")
    run(["ogr2ogr", "-overwrite", "-t_srs", src_proj4, final_src, clip_path])
    final = mktemp_output_path(out_dir, base, f".{fmt}")

    if fmt == "zip":
        pkg = os.path.join(tmpdir, "pkg")
        os.makedirs(pkg)
        shp_name = f"{base}.shp"
        run(["ogr2ogr", "-overwrite", os.path.join(pkg, shp_name), final_src])
        with zipfile.ZipFile(final, "w", zipfile.ZIP_DEFLATED) as z:
            for name in sorted(os.listdir(pkg)):
                z.write(os.path.join(pkg, name), name)
    elif fmt == "shp":
        run(["ogr2ogr", "-overwrite", final, final_src])
    elif fmt == "fgb":
        run(["ogr2ogr", "-overwrite", "-f", "FlatGeobuf", "-nlt", "PROMOTE_TO_MULTI",
             final, final_src])
    elif fmt == "gpkg":
        run(["ogr2ogr", "-overwrite", "-f", "GPKG", "-nlt", "PROMOTE_TO_MULTI",
             final, final_src])
    else:
        sys.exit(f"unknown format: {fmt}")
    return final


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("land", help="landmass layer (e.g. tl_2025_us_state.zip)")
    ap.add_argument("layer", help="arbitrary layer to buffer (e.g. tl_2025_us_uac20.zip)")
    ap.add_argument("meters", type=float, help="buffer distance in meters")
    ap.add_argument("--target-pct", type=float,
                    help="binary-search the max buffer keeping clipped area under P%%")
    ap.add_argument("--simplify", type=float, default=50.0, metavar="TOL",
                    help="simplify to TOL meters before buffering (default 50, 0 disables)")
    ap.add_argument("--format", dest="fmt", default=None,
                    choices=["zip", "shp", "fgb", "gpkg"],
                    help="output format (default: same as LAYER's extension)")
    ap.add_argument("--out-dir", default=None, help="output folder (default: LAYER's)")
    ap.add_argument("--us-land-km2", type=float, default=DEFAULT_US_LAND_KM2,
                    help=f"US landmass in km^2 (default {DEFAULT_US_LAND_KM2:,})")
    args = ap.parse_args()

    lon, lat, src_proj4 = layer_center_wgs84(args.layer)
    laea = f"+proj=laea +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs"

    layer_base = os.path.splitext(os.path.basename(args.layer))[0]
    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.layer))
    fmt = args.fmt or {
        ".zip": "zip", ".fgb": "fgb", ".gpkg": "gpkg",
    }.get(os.path.splitext(args.layer)[1].lower(), "shp")

    with tempfile.TemporaryDirectory(prefix="buf2coast.") as tmpdir:
        input_laea = os.path.join(tmpdir, "input_laea.shp")
        land_laea = os.path.join(tmpdir, "land_laea.shp")
        simp = os.path.join(tmpdir, "simp.shp")

        run(["ogr2ogr", "-overwrite", "-t_srs", laea, input_laea,
             layer_source_path(args.layer)], "reproject layer to equal-area projection")
        if args.simplify > 0:
            run(["ogr2ogr", "-overwrite", "-dialect", "SQLite", "-sql",
                 f"SELECT ST_SimplifyPreserveTopology(geometry, {args.simplify:g}) AS geom FROM input_laea",
                 simp, input_laea], f"simplify to {args.simplify:g} m")
        else:
            simp = input_laea

        run(["ogr2ogr", "-overwrite", "-t_srs", laea, land_laea,
             layer_source_path(args.land)], "reproject land layer")
        land_union = os.path.join(tmpdir, "land_union.shp")
        run(["ogr2ogr", "-overwrite", "-dialect", "SQLite", "-sql",
             "SELECT ST_Union(geometry) AS geom FROM land_laea",
             land_union, land_laea],
            "dissolve land layer into one polygon (don't clip on state lines)")

        def area_at(m, dissolve_raw=False):
            buf = os.path.join(tmpdir, "buf.shp")
            if m > 0:
                run(["ogr2ogr", "-overwrite", "-dialect", "SQLite", "-sql",
                     f"SELECT ST_Buffer(geometry, {m:g}) AS geom FROM simp",
                     buf, simp], f"buffer by {m:g} m")
            else:
                buf = simp
            clip = os.path.join(tmpdir, "clip.shp")
            run(["ogr2ogr", "-overwrite", "-clipdst", land_union, clip, buf],
                 "clip to land")

            def union_area(src):
                """Dissolve all features with ST_Union and return km^2, so
                overlapping buffers are not double-counted."""
                out = os.path.join(tmpdir, "union.shp")
                run(["ogr2ogr", "-overwrite", "-dialect", "SQLite", "-sql",
                     f"SELECT ST_Union(geometry) AS geom FROM {os.path.splitext(os.path.basename(src))[0]}",
                     out, src], "dissolve")
                ds = ogr.Open(out)
                lyr = ds.GetLayer()
                return sum(f.GetGeometryRef().Clone().GetArea() for f in lyr) / 1e6

            clip_km2 = union_area(clip)
            raw_km2 = union_area(buf) if dissolve_raw else None
            return raw_km2, clip_km2, clip

        def pct(km2):
            return km2 / args.us_land_km2 * 100.0

        if args.target_pct is not None:
            p0 = area_at(0)[1]
            if pct(p0) >= args.target_pct:
                sys.exit(f"clipped area is already {pct(p0):.3f}% of US landmass at 0 m; "
                         f"target is {args.target_pct}%")
            hi = 1000.0
            while True:
                _, c, _ = area_at(hi)
                print(f"  probe {hi:,.0f} m -> {pct(c):.3f}%", file=sys.stderr)
                if pct(c) >= args.target_pct or hi > 1e7:
                    break
                hi *= 10
            lo = 0.0
            it = 0
            while hi - lo > 1:
                it += 1
                mid = (lo + hi) / 2
                _, c, _ = area_at(mid)
                print(f"  [{it}] {mid:,.0f} m -> {pct(c):.3f}%", file=sys.stderr)
                if pct(c) < args.target_pct:
                    lo = mid
                else:
                    hi = mid
            meters = lo
            raw_km2, clip_km2, clip = area_at(meters, dissolve_raw=True)
        else:
            meters = args.meters
            raw_km2, clip_km2, clip = area_at(meters, dissolve_raw=True)

        final = package(clip, out_dir, layer_base, fmt, src_proj4, tmpdir)

    print(f"land: {args.land}   layer: {args.layer}   buffer: {meters:,.0f} m")
    print(f"projection center: ({lon:.1f}, {lat:.1f})   "
          f"US landmass: {args.us_land_km2:,.0f} km^2")
    if args.simplify > 0:
        print(f"simplified to {args.simplify:g} m before buffering")
    table = [
        ["raw buffer (unclipped)", raw_km2, f"{pct(raw_km2):.3f}%"],
        ["clipped to land", clip_km2, f"{pct(clip_km2):.3f}%"],
    ]
    print(tabulate(table, headers=["Measure", "Area km^2", "% of US landmass"],
                   tablefmt="simple", floatfmt=",.1f"))
    if args.target_pct is not None:
        print(f"\nlargest buffer under {args.target_pct}% of US landmass: "
              f"{meters:,.0f} m ({meters / 1000:,.2f} km)")
    print(f"output written to: {final}")


if __name__ == "__main__":
    main()
