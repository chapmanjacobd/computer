#!/usr/bin/env python3

import difflib
import os
import re
import subprocess
import sys
from collections import defaultdict


def get_staged_files():
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-status', '--staged', '-z'],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
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
        filename = staged_files_list[i + 1]
        files_by_status[status].append(filename)

    return files_by_status


def get_diff_stats(filename):
    try:
        result = subprocess.run(
            ['git', 'diff', '--staged', '--numstat', "--", ":/" + filename],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
        )
        match = re.match(r'(\d+)\s+(\d+)\s+.*', result.stdout)
        if match:
            return {'added': int(match.group(1)), 'deleted': int(match.group(2))}

    except subprocess.CalledProcessError as e:
        print(f"Error getting diff for {filename}: {e}", file=sys.stderr)
    return {}


def track_moved(added_lines: list[str], removed_lines: list[str]):
    added = list(added_lines)
    removed = list(removed_lines)
    modified = []
    moved = []
    for line in list(added_lines):
        if line in removed:
            added.remove(line)
            removed.remove(line)
            moved.append(line)

    remaining_added = list(added)
    for added_line in remaining_added:
        best_match = None
        highest_ratio = 0.0

        for removed_line in list(removed):
            s = difflib.SequenceMatcher(None, added_line, removed_line)
            ratio = s.ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = removed_line

        if highest_ratio > 0.8:
            modified.append(added_line)
            added.remove(added_line)
            if best_match in removed:
                removed.remove(best_match)

    return added, removed, modified, moved


def get_diff_line(filename):
    try:
        result = subprocess.run(
            ['git', 'diff', '--staged', '--unified=0', "--", ":/" + filename],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
        )
    except subprocess.CalledProcessError as e:
        print(f"Error getting diff lines for {filename}: {e}", file=sys.stderr)
    else:
        added_lines = []
        removed_lines = []
        for line in result.stdout.splitlines():
            if line.startswith('+') and not line.startswith('+++'):
                line = line[1:]  # strip the +/- prefix
                line = line.strip()
                if line:
                    added_lines.append(line)
            elif line.startswith('-') and not line.startswith('---'):
                line = line[1:]  # strip the +/- prefix
                line = line.strip()
                if line:
                    removed_lines.append(line)

        added, removed, modified, moved = track_moved(added_lines, removed_lines)
        # print(added, removed, moved)

        parts = []
        if added:
            added_text = "⏎".join(added)
            if len(added_text) <= 80:
                parts.append(f"Added text '{added_text}'")
            else:
                parts.append(f"Added {len(added)} lines")
        if removed:
            removed_text = "⏎".join(removed)
            if len(removed_text) <= 80:
                parts.append(f"Deleted text '{removed_text}'")
            else:
                parts.append(f"Deleted {len(removed)} lines")
        if modified:
            modified_text = "⏎".join(modified)
            if len(modified_text) <= 80:
                parts.append(f"Modified text to '{modified_text}'")
            else:
                parts.append(f"Modified {len(modified)} lines")
        if moved:
            moved_text = "⏎".join(moved)
            if len(moved_text) <= 80:
                parts.append(f"Moved text '{moved_text}'")
            else:
                parts.append(f"Moved {len(moved)} lines")

        return "; ".join(parts)


def format_single_file_message(filename):
    diff_line = get_diff_line(filename)
    if diff_line:
        is_short_change = len(diff_line) < 120
        if is_short_change:
            return f"{os.path.basename(filename)}: {diff_line}"

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
            message_parts.append(f"{len(file_list)} files in {folder}")
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
    for status, prefix in prefix_map.items():
        if status in files_by_status:
            formatted_list = format_files_for_message(files_by_status[status])
            if formatted_list:
                message_parts.append(f"{prefix} {formatted_list}")

    for status, files in files_by_status.items():
        if status.startswith('R'):
            formatted_list = format_files_for_message(files)
            if formatted_list:
                message_parts.append(f"Renamed {formatted_list}")

    return '; '.join(message_parts)


def main():
    files_by_status = get_staged_files()
    message = build_commit_message(files_by_status)
    if message:
        print(message)


if __name__ == "__main__":
    main()
