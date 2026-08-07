#!/usr/bin/env python3
"""Compute total land area (km^2) of vector layers and compare them.

Generalizable: accepts any number of shapefiles / zipped shapefiles,
computes each layer's total area in km^2 using an equal-area projection
centered on the layer's own extent (works for any region on Earth),
unions the projected geometries before measuring area to avoid counting
overlaps more than once,
and prints a comparison table with tabulate.

Usage:
    area.py [--us-land-km2 N] [--overlaps] LAYER1 [LAYER2 ...]

Examples:
    area.py tl_2025_us_uac20.zip tl_2025_us_metdiv.zip
    area.py states.shp cities.gpkg regions.shp

Options:
    --us-land-km2 N   Total US landmass in km^2 to use for the
                      "% of US landmass" column (default: 9147593,
                      the Census land area of the 50 states + DC).
    --overlaps        Also show naive summed area and overlap area.
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


def layer_stats(path):
    ds, lyr = open_layer(path)
    src = lyr.GetSpatialRef()
    if src is None:
        sys.exit(f"{path}: layer has no spatial reference; cannot compute area")
    src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    env = lyr.GetExtent()  # (minX, maxX, minY, maxY) in source units
    cx, cy = (env[0] + env[1]) / 2.0, (env[2] + env[3]) / 2.0

    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(4326)
    wgs84.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    tx_to_wgs84 = osr.CoordinateTransformation(src, wgs84)
    lon, lat, _ = tx_to_wgs84.TransformPoint(cx, cy)

    dst = osr.SpatialReference()
    dst.ImportFromProj4(
        f"+proj=laea +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs"
    )
    dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    tx = osr.CoordinateTransformation(src, dst)

    naive_m2 = 0.0
    unioned = None
    nfeat = 0
    for feat in lyr:
        geom = feat.GetGeometryRef()
        if geom is None or geom.IsEmpty():
            continue
        g = geom.Clone()
        g.Transform(tx)
        naive_m2 += g.GetArea()
        unioned = g if unioned is None else unioned.Union(g)
        nfeat += 1
    unioned_m2 = unioned.GetArea() if unioned is not None else 0.0
    return nfeat, unioned_m2 / 1e6, naive_m2 / 1e6


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("layers", nargs="+", help="paths to vector layers (shp, zip, gpkg, ...)")
    ap.add_argument("--us-land-km2", type=float, default=DEFAULT_US_LAND_KM2,
                    help=f"US landmass in km^2 (default {DEFAULT_US_LAND_KM2:,})")
    ap.add_argument("--overlaps", action="store_true",
                    help="also show naive summed area and overlap area")
    args = ap.parse_args()

    rows = []
    for path in args.layers:
        n, km2, naive_km2 = layer_stats(path)
        name = path.rsplit("/", 1)[-1]
        rows.append({
            "path": path,
            "name": name,
            "features": n,
            "km2": km2,
            "naive_km2": naive_km2,
            "overlap_km2": naive_km2 - km2,
        })

    headers = ["Layer", "Features", "Area km^2", "% of US landmass"]
    table = []
    for r in rows:
        pct_us = r["km2"] / args.us_land_km2 * 100
        table.append([r["name"], r["features"], f"{r['km2']:,.1f}", f"{pct_us:.3f}%"])

    if len(rows) > 1:
        base = rows[0]
        headers.append("% vs baseline")
        for r, row in zip(rows, table):
            if r is base:
                row.append("—")
            else:
                row.append(f"{(r['km2'] - base['km2']) / base['km2'] * 100:+.2f}%")

    print(tabulate(table, headers=headers, tablefmt="grid"))
    print(f"US landmass used: {args.us_land_km2:,.0f} km^2")

    if args.overlaps:
        overlap_table = []
        for r in rows:
            for measure, km2 in (
                ("unioned", r["km2"]),
                ("naive", r["naive_km2"]),
                ("overlap", r["overlap_km2"]),
            ):
                overlap_table.append([
                    r["name"],
                    measure,
                    r["features"],
                    f"{km2:,.1f}",
                    f"{km2 / args.us_land_km2 * 100:.3f}%",
                ])
        print("\noverlap details:")
        print(tabulate(
            overlap_table,
            headers=["Layer", "Measure", "Features", "Area km^2", "% of US landmass"],
            tablefmt="grid",
        ))

    if len(rows) > 1:
        print(f"\nbaseline: {base['name']}")
        print("pairwise: '% bigger than' (row layer vs column layer)")
        header = [""] + [r["name"] for r in rows]
        mat = []
        for a in rows:
            line = [a["name"]]
            for b in rows:
                if a is b:
                    line.append("—")
                else:
                    line.append(f"{(a['km2'] - b['km2']) / b['km2'] * 100:+.2f}%")
            mat.append(line)
        print(tabulate(mat, headers=header, tablefmt="grid"))


if __name__ == "__main__":
    main()
