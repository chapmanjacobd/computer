#!/usr/bin/python
from pathlib import Path
from pprint import pprint

import yaml
from library.utils import argparse_utils


def main():
    parser = argparse_utils.ArgumentParser()
    parser.add_argument("yaml_file", type=Path)
    args = parser.parse_args()

    with args.yaml_file.open() as f:
        data = yaml.safe_load(f)

    pprint(data)


if __name__ == "__main__":
    main()
