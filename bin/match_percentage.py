#!/usr/bin/python

import argparse

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a term in a file and print the percentage of occurrences.")
    parser.add_argument("file_path", help="Path to the file to search.")
    parser.add_argument("search_term", help="The term to search for.")

    args = parser.parse_args()

    grep_file(args.file_path, args.search_term)