#!/usr/bin/python
from pathlib import Path

import yaml
from hera.workflows.models import Workflow
from rich import print
from library.utils import argparse_utils


def main():
    parser = argparse_utils.ArgumentParser()
    parser.add_argument("yaml_file", type=Path)
    args = parser.parse_args()

    with args.yaml_file.open() as f:
        workflow = Workflow.parse_obj(yaml.safe_load(f))

    print(workflow)


if __name__ == "__main__":
    main()
