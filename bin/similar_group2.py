#!/usr/bin/python3
import argparse
from collections import defaultdict
import difflib
from typing import List, Dict, Any

from tabulate import tabulate

from library.utils import argparse_utils, processes, strings, iterables


def main():
    parser = argparse_utils.ArgumentParser(description='Relaxed group-by using difflib for two files')
    parser.add_argument('--ignore-case', '-i', action='store_true', help='Ignore upper-case')
    parser.add_argument('--minimum-similarity', '-m', type=float, default=0.6)
    parser.add_argument('--maximum-similarity', '-M', type=float, default=1.0)

    parser.add_argument('input_path_left', type=argparse.FileType('r'), help='Path to the left input file')
    parser.add_argument('input_path_right', type=argparse.FileType('r'), help='Path to the right input file')
    args = parser.parse_args()

    if not (0.0 <= args.minimum_similarity <= 1.0):
        raise ValueError("minimum-similarity must be between 0.0 and 1.0")
    if not (0.0 <= args.maximum_similarity <= 1.0):
        raise ValueError("maximum-similarity must be between 0.0 and 1.0")

    def s(line: str) -> str:
        return strings.path_to_sentence(line.lower() if args.ignore_case else line)

    lines: List[Dict[str, Any]] = []
    for i, line in enumerate(args.input_path_left.readlines()):
        line  = line.strip()
        if line:
            lines.append({'original_line': line, 'lineno': i + 1, 'source': 'left'})

    for i, line in enumerate(args.input_path_right.readlines()):
        line  = line.strip()
        if line:
            lines.append({'original_line': line, 'lineno': i + 1, 'source': 'right'})

    if not lines:
        processes.no_media_found()

    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for line_data in lines:
        found_group = False
        current_line_text = s(args, line_data['original_line'])

        for canonical_line, group_list in groups.items():
            canonical_line_text = s(args, canonical_line)
            matcher = difflib.SequenceMatcher(None, current_line_text, canonical_line_text)

            if args.maximum_similarity >= matcher.ratio() >= args.minimum_similarity:
                found_group = True
                groups[canonical_line].append(line_data)
                break
        if not found_group:
            groups[line_data['original_line']] = [line_data]

    table_data = []
    for canonical_line, group_list in groups.items():
        min_lineno = min(item['lineno'] for item in group_list)

        in_left = 'X' if any(item['source'] == 'left' for item in group_list) else ''
        in_right = 'X' if any(item['source'] == 'right' for item in group_list) else ''

        if len(group_list) > 1:
            group_lines = ['L ' if item['source'] == 'left' else 'R ' + item['original_line'] for item in group_list]
        else:
            group_lines = [item['original_line'] for item in group_list]
        combined_lines = "\n".join(group_lines)

        table_data.append([min_lineno, in_left, in_right, combined_lines])

    # Sort the table data by the minimum line number to preserve a sense of original order
    table_data.sort(key=lambda x: x[0])

    headers = ["Original Line Number", "Left File", "Right File", "Similar Lines"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


if __name__ == '__main__':
    main()
