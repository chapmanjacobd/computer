#!/usr/bin/python3
import difflib
from pathlib import Path

from library.utils import argparse_utils, strings


def search_in_file(args, path):
    with open(path, 'r') as file:
        for line_number, line_text in enumerate(file, start=1):
            line_text = line_text.rstrip('\n')

            for search_arg in args.search_term.splitlines():
                similarity_ratio = difflib.SequenceMatcher(
                    None, search_arg, strings.path_to_sentence(line_text.lower() if args.ignore_case else line_text)
                ).ratio()

                if args.maximum_similarity >= similarity_ratio >= args.minimum_similarity:
                    output = f"{strings.safe_percent(similarity_ratio)}\t{path}\t{line_text}"
                    if args.line_number:
                        output = f"{strings.safe_percent(similarity_ratio)}\t{path}:{line_number}\t{line_text}"
                    print(output)


def main():
    parser = argparse_utils.ArgumentParser(description='Similar to grep using difflib')
    parser.add_argument('--ignore-case', '-i', action='store_true', help='Ignore upper-case')
    parser.add_argument('--line-number', action='store_true', help='Print line numbers along with output')
    parser.add_argument('--minimum-similarity', '-m', type=float, default=0.3)
    parser.add_argument('--maximum-similarity', '-M', type=float, default=1.0)

    parser.add_argument('search_term', help='Search term')
    parser.add_argument('files', nargs='+', help='List of files or directories')
    args = parser.parse_args()

    p = Path(args.search_term)
    if p.is_file():
        args.search_term = p.read_text()

    args.search_term = strings.path_to_sentence(args.search_term.lower())
    if args.ignore_case:
        args.search_term = args.search_term.lower()

    for file in args.files:
        p = Path(file)
        if p.is_dir():
            for path in p.rglob('*'):
                if path.is_file():
                    search_in_file(args, path)
        else:
            search_in_file(args, file)


if __name__ == '__main__':
    main()
