#!/usr/bin/env python3

import subprocess
import sys
import os
from collections import defaultdict

def get_staged_files():
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-status', '--staged', '-z'],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error calling git: {e}", file=sys.stderr)
        sys.exit(1)

    output = result.stdout.strip()
    if not output:
        return defaultdict(list)

    staged_files_list = output.split('\x00')
    files_by_status = defaultdict(list)

    for i in range(0, len(staged_files_list) - 1, 2):
        status = staged_files_list[i]
        filename = staged_files_list[i+1]
        files_by_status[status].append(filename)

    return files_by_status

def format_files_for_message(files):
    if not files:
        return ""

    folders = defaultdict(list)
    for file in files:
        directory = os.path.dirname(file) or '.'
        folders[directory].append(file)

    message_parts = []
    for folder, file_list in folders.items():
        if len(file_list) > 3:
            message_parts.append(f"{len(file_list)} files from {folder}")
        else:
            message_parts.extend([os.path.basename(f) for f in file_list])

    return ', '.join(message_parts)

def build_commit_message(files_by_status):
    message_parts = []

    prefix_map = {
        'A': 'Added',
        'M': 'Modified',
        'D': 'Deleted',
    }

    if 'A' in files_by_status:
        formatted_list = format_files_for_message(files_by_status['A'])
        if formatted_list:
            message_parts.append(f"{prefix_map['A']} {formatted_list}")

    if 'M' in files_by_status:
        formatted_list = format_files_for_message(files_by_status['M'])
        if formatted_list:
            message_parts.append(f"{prefix_map['M']} {formatted_list}")

    if 'D' in files_by_status:
        formatted_list = format_files_for_message(files_by_status['D'])
        if formatted_list:
            message_parts.append(f"{prefix_map['D']} {formatted_list}")

    return '; '.join(message_parts)

def main():
    files_by_status = get_staged_files()
    message = build_commit_message(files_by_status)
    print(message)

if __name__ == "__main__":
    main()
