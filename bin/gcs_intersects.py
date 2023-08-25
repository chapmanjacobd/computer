#!/usr/bin/python3

import argparse
import re

import geopandas as gpd
from google.cloud import storage
from osgeo import gdal
from shapely.geometry import box

parser = argparse.ArgumentParser()
parser.add_argument('gcs_folder', help='Top level folder in GCS bucket to search')
parser.add_argument('vector_file', help='Vector file for intersection')
args = parser.parse_args()

vector = gpd.read_file(args.vector_file)


def split_gcs(gcs_path):
    match = re.match(r'gs://([a-zA-Z0-9_\-\.]+)/([\S]*)', gcs_path)
    if match:
        bucket = match.group(1)
        prefix = match.group(2)
    else:
        raise ValueError(f'Invalid GCS path: {gcs_path}')

    return bucket, prefix


client = storage.Client()
bucket, prefix = split_gcs(args.gcs_folder)
blobs = client.list_blobs(bucket, prefix=prefix)

for blob in blobs:
    if blob.name.endswith('.tif'):
        ds = gdal.Open(f'/vsigs/{blob.bucket.name}/{blob.name}')
        gt = ds.GetGeoTransform()
        x_size = ds.RasterXSize
        y_size = ds.RasterYSize

        minx, maxx, miny, maxy = gt[0], gt[0] + gt[1] * x_size, gt[3], gt[3] + gt[5] * y_size

        if vector.intersects(box(minx, miny, maxx, maxy)).any():
            print(f'gs://{blob.bucket.name}/{blob.name}')
