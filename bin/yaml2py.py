#!/usr/bin/python
import argparse
from pathlib import Path
from pprint import pprint

import yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("yaml_file", type=Path)
    args = parser.parse_args()

    with args.yaml_file.open() as f:
        data = yaml.safe_load(f)

    pprint(data)


if __name__ == "__main__":
    main()
