#!/usr/bin/env python3
# from https://gitlab.com/hydrargyrum/attic/
# SPDX-License-Identifier: WTFPL

import json
import sys

import yaml


fp = sys.stdin
if len(sys.argv) == 2:
	fp = open(sys.argv[1])

with fp:
	json.dump(yaml.safe_load(fp), sys.stdout)
print()  # final newline
