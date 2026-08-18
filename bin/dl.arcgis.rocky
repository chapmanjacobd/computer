#!/usr/bin/env python3

import argparse
import csv
import json
import mimetypes
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

LAYER_URL = (
    "https://services1.arcgis.com/Ggva1SWphWGX4bb8/arcgis/rest/services/RocyOnParade2020_WFL1/FeatureServer/0/query"
)
DEFAULT_WHERE = "Retired = 'No'"
USER_AGENT = "rocky-export/1.0"


def fetch_json(url: str, params: dict[str, object]) -> dict[str, object]:
    query = urlencode(params)
    request = Request(f"{url}?{query}", headers={"User-Agent": USER_AGENT})
    with urlopen(request) as response:
        return json.load(response)


def fetch_features(where: str) -> list[dict[str, object]]:
    features: list[dict[str, object]] = []
    offset = 0
    page_size = 2000

    while True:
        payload = fetch_json(
            LAYER_URL,
            {
                "where": where,
                "outFields": "*",
                "returnGeometry": "false",
                "f": "json",
                "resultOffset": offset,
                "resultRecordCount": page_size,
            },
        )

        batch = payload.get("features", [])
        if not isinstance(batch, list) or not batch:
            break

        features.extend(batch)
        if not payload.get("exceededTransferLimit"):
            break
        offset += len(batch)

    return features


def sanitize_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._") or "image"


def infer_extension(headers, image_url: str) -> str:
    disposition = headers.get("Content-Disposition", "")
    match = re.search(r'filename="?([^";]+)"?', disposition)
    if match:
        return Path(match.group(1)).suffix or ""

    content_type = headers.get_content_type()
    if content_type:
        guessed = mimetypes.guess_extension(content_type)
        if guessed == ".jpe":
            return ".jpg"
        if guessed:
            return guessed

    suffix = Path(urlparse(image_url).path).suffix
    return suffix or ".bin"


def download_image(image_url: str, output_dir: Path, stem: str) -> Path:
    request = Request(image_url, headers={"User-Agent": USER_AGENT})
    with urlopen(request) as response:
        extension = infer_extension(response.headers, image_url)
        output_path = output_dir / f"{stem}{extension}"
        if output_path.exists():
            return output_path

        data = response.read()

    output_path.write_bytes(data)
    return output_path


def build_rows(features: list[dict[str, object]], images_dir: Path, relative_to: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    images_dir.mkdir(parents=True, exist_ok=True)

    for feature in features:
        attributes = dict(feature.get("attributes", {}))
        image_url = attributes.get("Image_Link") or ""
        relative_path = ""

        if image_url:
            object_id = attributes.get("OBJECTID", "unknown")
            item_id = attributes.get("Id", "unknown")
            name = attributes.get("Name", "poi")
            stem = sanitize_filename(f"{object_id}_{item_id}_{name}")
            try:
                image_path = download_image(str(image_url), images_dir, stem)
                relative_path = os.path.relpath(image_path, start=relative_to).replace("\\", "/")
            except (HTTPError, URLError) as exc:
                print(f"warning: could not download {image_url}: {exc}", file=sys.stderr)

        attributes["relative_image_path"] = relative_path
        rows.append(attributes)

    return rows


def write_csv(rows: list[dict[str, object]], csv_path: Path) -> None:
    if not rows:
        raise SystemExit("No rows returned from the feature service.")

    fieldnames = list(rows[0].keys())
    for row in rows[1:]:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Rocky on Parade POIs to CSV and download linked images.")
    parser.add_argument(
        "--where",
        default=DEFAULT_WHERE,
        help=f"ArcGIS SQL where clause (default: {DEFAULT_WHERE!r})",
    )
    parser.add_argument(
        "--csv",
        default="rocky_pois.csv",
        help="Output CSV path (default: rocky_pois.csv)",
    )
    parser.add_argument(
        "--images-dir",
        default="images",
        help="Directory for downloaded images (default: images)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv)
    images_dir = Path(args.images_dir)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    features = fetch_features(args.where)
    rows = build_rows(features, images_dir, csv_path.parent)
    write_csv(rows, csv_path)

    print(f"Wrote {csv_path} with {len(rows)} rows.")
    print(f"Downloaded images to {images_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
