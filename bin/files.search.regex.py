#!/usr/bin/python

import re

from library.utils import argparse_utils


def grep_file(file_path, search_term):
    try:
        with open(file_path, 'r') as file:
            total_lines = 0
            search_count = 0
            for line in file:
                total_lines += 1
                if search_term in line:
                    search_count += 1

            if total_lines == 0:
                print("Error: File is empty.")
            else:
                percentage = (search_count / total_lines) * 100
                print(f"The search term '{search_term}' appears in {percentage:.2f}% of the file.")

    except FileNotFoundError:
        print("Error: File not found.")


def print_matches(file_path, search_term):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        total_lines = len(lines)
        for i, line in enumerate(lines):
            if re.search(search_term, line):
                print('\t'.join([f"L{i+1} / {total_lines}", f"{round((i+1)/total_lines*100, 2)}%", line.strip()]))


if __name__ == "__main__":
    parser = argparse_utils.ArgumentParser(
        description="Search for a term in a file and print the percentage of occurrences."
    )
    parser.add_argument("file_path", help="Path to the file to search.")
    parser.add_argument("search_term", help="The term to search for.")

    args = parser.parse_args()

    print_matches(args.file_path, args.search_term)
    grep_file(args.file_path, args.search_term)
