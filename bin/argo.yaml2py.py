#!/usr/bin/python
import argparse
import yaml
from pathlib import Path
from rich import print
from hera.workflows.models import Workflow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("yaml_file", type=Path)
    args = parser.parse_args()

    with args.yaml_file.open() as f:
        workflow = Workflow.parse_obj(yaml.safe_load(f))

    print(workflow)


if __name__ == "__main__":
    main()
