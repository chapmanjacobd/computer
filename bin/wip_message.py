#!/usr/bin/env python3

import subprocess
import sys
import os
import argparse
from collections import defaultdict
import re

def get_staged_files():
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-status', '--staged', '-z'],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
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
        status = staged_files_list[i].strip()
        filename = staged_files_list[i+1]
        files_by_status[status].append(filename)

    return files_by_status

def get_diff_stats(filename):
    try:
        result = subprocess.run(
            ['git', 'diff', '--staged', '--numstat', filename],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        match = re.match(r'(\d+)\s+(\d+)\s+.*', result.stdout)
        if match:
            return {
                'added': int(match.group(1)),
                'deleted': int(match.group(2))
            }

    except subprocess.CalledProcessError as e:
        print(f"Error getting diff for {filename}: {e}", file=sys.stderr)
    return {}

def format_single_file_message(filename):
    diff_stats = get_diff_stats(filename)
    if diff_stats:
        parts = []
        if diff_stats.get('added', 0) > 0:
            parts.append(f"{diff_stats['added']} lines added")
        if diff_stats.get('deleted', 0) > 0:
            parts.append(f"{diff_stats['deleted']} lines deleted")

        if parts:
            return f"{os.path.basename(filename)}: {', '.join(parts)}"

    return os.path.basename(filename)

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
    all_files = [f for files in files_by_status.values() for f in files]
    if len(all_files) == 1:
        return format_single_file_message(all_files[0])

    prefix_map = {
        'A': 'Added',
        'M': 'Modified',
        'D': 'Deleted',
    }

    message_parts = []
    for status, files in files_by_status.items():
        if status.startswith('R'):
            formatted_list = format_files_for_message(files)
            if formatted_list:
                message_parts.append(f"Renamed {formatted_list}")
        elif status in prefix_map:
            formatted_list = format_files_for_message(files)
            if formatted_list:
                message_parts.append(f"{prefix_map[status]} {formatted_list}")

    return '; '.join(message_parts)


def main():
    files_by_status = get_staged_files()
    message = build_commit_message(files_by_status)
    print(message)

if __name__ == "__main__":
    main()
