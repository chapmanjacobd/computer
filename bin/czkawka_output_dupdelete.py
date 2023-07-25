#!/usr/bin/python3

import re
import os
import argparse


def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content


def extract_groups(content):
    first_newline_index = content.find("\n")

    if first_newline_index != -1 and "similar friends" in content[:first_newline_index].strip().lower():
        content = content[first_newline_index + 1 :]

    groups = re.split(r"(-+MESSAGES-+\n+)", content)[0].split("\n\n")
    return groups


def extract_paths_and_sizes(group_content):
    paths_and_sizes = []
    for match in group_content.split('\n'):
        size_str = match.split(" - ")[1]
        size_value, size_unit = float(size_str.split()[0]), size_str.split()[1]
        if size_unit == "GiB":
            size_value *= 1024
        elif size_unit == "KiB":
            size_value /= 1024
        paths_and_sizes.append({'path': match.split(" - ")[0], 'size_mb': size_value})
    return paths_and_sizes


def group_and_delete(groups):
    for group_content in groups:
        if group_content == '':
            continue

        group = extract_paths_and_sizes(group_content)
        group.sort(key=lambda x: x['size_mb'], reverse=True)
        largest_path = group[0]['path']

        if os.path.exists(largest_path):
            for d in group[1:]:
                path = d['path']
                if os.path.exists(path):
                    os.remove(path)
                    print(f"Deleted: {path}")
                else:
                    print(f"Duplicate not found: {path}")
        else:
            print(f"Original not found: {largest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup duplicate files based on their sizes.")
    parser.add_argument("file_path", help="Path to the text file containing the file list.")
    args = parser.parse_args()

    file_path = args.file_path
    content = read_file(file_path)
    groups = extract_groups(content)
    group_and_delete(groups)
