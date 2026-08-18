#!/usr/bin/python3
import json
import sys
from collections import defaultdict


def filter_dicts(dicts):
    counter = defaultdict(int)
    for d in dicts:
        for key, value in d.items():
            counter[(key, str(value))] += 1

    filtered_dicts = []
    for d in dicts:
        filtered_d = {}
        for key, value in d.items():
            if counter[(key, str(value))] < len(dicts):
                filtered_d[key] = value
        filtered_dicts.append(filtered_d)

    return filtered_dicts


def filter_json_dicts():
    input_json = json.load(sys.stdin)
    filtered_dicts = filter_dicts(input_json)
    print(json.dumps(filtered_dicts))


if __name__ == "__main__":
    filter_json_dicts()
