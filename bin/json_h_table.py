#!/usr/bin/python3
import json
import sys
from tabulate import tabulate

def h_table():
    input_json = json.load(sys.stdin)

    if isinstance(input_json, list) and all(isinstance(i, dict) for i in input_json):
        print(tabulate(input_json, tablefmt="simple", headers="keys", showindex=False))
    else:
        print("Input should be a list of dictionaries.")

if __name__ == "__main__":
    h_table()
