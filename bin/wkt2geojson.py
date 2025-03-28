#!/usr/bin/python3
import sys

import geopandas as gpd
from library.utils import argparse_utils

parser = argparse_utils.ArgumentParser()
parser.add_argument('--s_srs', '-s_srs', default='EPSG:4326', help='SRS of source vector')
args = parser.parse_args()

wkt = sys.stdin.read()

gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries.from_wkt([wkt], crs=args.s_srs))
gdf = gdf.to_crs(epsg=4326)

print(gdf.to_json())
