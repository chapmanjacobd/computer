#!/usr/bin/python3

import argparse
import json
import sys
from datetime import datetime

import tabulate

parser = argparse.ArgumentParser()
parser.add_argument("file", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
args = parser.parse_args()


data = json.load(args.file)

rows = []
for item in data:
    pods = []
    try:
        pods = item["status"]["nodes"].values()
    except KeyError:
        pass

    last_succeeded_pod = None
    try:
        last_succeeded_pod = max(
            (p for p in pods if p["phase"] == "Succeeded"), key=lambda x: datetime.fromisoformat(x["finishedAt"])
        )
    except ValueError:
        pass

    running_pod = None
    try:
        running_pod = max(
            (p for p in pods if p["phase"] == "Running"), key=lambda x: datetime.fromisoformat(x["startedAt"])
        )
    except ValueError:
        pass

    rows.append(
        {
            "Name": item["metadata"]["name"],
            "Status": item["metadata"]["status"],
            "Progress": item["status"]["progress"],
            "Started At": item["status"]["startedAt"],
            "Last Succeeded Pod": last_succeeded_pod["displayName"] + " - " + last_succeeded_pod["templateName"],
            "Running Pod": running_pod["displayName"] + " - " + running_pod["templateName"] if running_pod else "",
        }
    )

# Print table
headers = rows[0].keys()
print(tabulate.tabulate(rows, headers="keys"))
