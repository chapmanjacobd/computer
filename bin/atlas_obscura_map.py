#!/usr/bin/python3
import argparse
from library.utils import argparse_utils
import json
from pathlib import Path

from library.createdb import site_add
from library.utils import db_utils, objects
from library.utils.log_utils import log


def parse_args() -> argparse.Namespace:
    parser = argparse_utils.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0)

    parser.add_argument("database")
    parser.add_argument("json_path")
    args = parser.parse_args()

    Path(args.database).touch()
    args.db = db_utils.connect(args)
    log.info(objects.dict_filter_bool(args.__dict__))

    return args


args = parse_args()

for p in Path(args.json_path).glob('*.json'):
    d = json.load(open(p))

    nearby_places = d.pop('nearby_places', None) or []
    nearby_foods = d.pop('nearby_foods', None) or []

    tables = site_add.nosql_to_sql([d, *nearby_places, *nearby_foods])

    for table in tables:
        args.db["media"].upsert_all(
            table['data'],
            alter=True,
            pk="id",
        )
