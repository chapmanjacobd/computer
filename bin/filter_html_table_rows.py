#!/usr/bin/python3
from bs4 import BeautifulSoup
from xklb.utils import argparse_utils

parser = argparse_utils.ArgumentParser()
parser.add_argument("filepath", help="HTML file path")
parser.add_argument("search_str", help="Text or partial HTML to search for")
parser.add_argument(
    "-v", "--invert-match", action="store_true", help="Print lines/rows containing the match instead of excluding them"
)
args = parser.parse_args()

with open(args.filepath) as fp:
    soup = BeautifulSoup(fp, 'html.parser')

for row in soup.find_all('tr'):
    match = args.search_str in str(row)
    if match and args.invert_match:
        continue
    elif not match and not args.invert_match:
        continue
    else:
        print(row)
