#!/usr/bin/python3

import functools
import re

import geopandas as gpd
from google.cloud import storage
from osgeo import gdal
from shapely.geometry import box
from xklb.utils import argparse_utils

parser = argparse_utils.ArgumentParser()
parser.add_argument('gcs_folder', help='Top level folder in GCS bucket to search')
parser.add_argument('vector_file', help='Vector file for intersection')
args = parser.parse_args()


def split_gcs(gcs_path):
    match = re.match(r'gs://([a-zA-Z0-9_\-\.]+)/([\S]*)', gcs_path)
    if match:
        bucket = match.group(1)
        prefix = match.group(2)
    else:
        raise ValueError(f'Invalid GCS path: {gcs_path}')

    return bucket, prefix


gdf: gpd.GeoDataFrame = gpd.read_file(args.vector_file)


@functools.lru_cache(maxsize=32)
def reproject_vector(srs):
    return gdf.to_crs(srs)


client = storage.Client()
bucket, prefix = split_gcs(args.gcs_folder)
blobs = client.list_blobs(bucket, prefix=prefix)

for blob in blobs:
    if blob.name.endswith('.tif'):
        ds: gdal.Dataset = gdal.Open(f'/vsigs/{blob.bucket.name}/{blob.name}')
        gt = ds.GetGeoTransform()
        x_size = ds.RasterXSize
        y_size = ds.RasterYSize
        srs = ds.GetSpatialRef()

        minx, maxx, miny, maxy = gt[0], gt[0] + gt[1] * x_size, gt[3], gt[3] + gt[5] * y_size

        if reproject_vector(srs.ExportToWkt()).intersects(box(minx, miny, maxx, maxy)).any():  # type: ignore
            print(f'gs://{blob.bucket.name}/{blob.name}')
