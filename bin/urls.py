#!/usr/bin/python3
import argparse
import re
import sys


def process_stream(args):
    url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
    for line in args.input:
        for url in url_pattern.findall(line):
            cleaned_url = url.rstrip('.,;:)]}')
            if cleaned_url:
                print(cleaned_url)


def main():
    parser = argparse.ArgumentParser(description="Extract URLs from line-delimited stdin.")
    parser.add_argument("input", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    args = parser.parse_args()
    process_stream(args)


if __name__ == "__main__":
    main()
