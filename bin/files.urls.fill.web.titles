#!/usr/bin/python3
import os
import shutil
import sys
import tempfile

from library.utils import arggroups, argparse_utils, shell_utils, web


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.requests(parser)
    parser.add_argument("--local-html", action="store_true", help="Treat paths as Local HTML files")
    arggroups.selenium(parser)
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser)
    args = parser.parse_intermixed_args()
    arggroups.args_post(args, parser)

    web.requests_session(args)  # prepare requests session
    arggroups.selenium_post(args)

    return args


def process_music_list(input_lines: list[str]) -> list[str]:
    output_lines = []
    for line in input_lines:
        if line.startswith(("https://", "http://")) and "  # " not in line:
            page_title = web.get_title(args, line)
            output_lines.append(f"{line}  # {page_title}")
        else:
            output_lines.append(line)
    return output_lines


def write_and_replace(file_path: str, new_content: list[str]):
    temp_file = None
    try:
        temp_dir = os.path.dirname(os.path.abspath(file_path))
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, dir=temp_dir) as temp_file:
            temp_file.writelines(s + "\n" for s in new_content)

        shutil.move(temp_file.name, file_path)

    except Exception as e:
        print(f"An error occurred while writing to '{file_path}': {e}")
        if temp_file and os.path.exists(temp_file.name):
            os.remove(temp_file.name)
        raise


if __name__ == "__main__":
    args = parse_args()

    if args.selenium:
        web.load_selenium(args)
    try:
        for file_path in shell_utils.gen_paths(args):
            if not os.path.exists(file_path):
                print(f"Error: File not found at '{file_path}'. Skipping.", file=sys.stderr)
                continue

            with open(file_path, 'r') as file:
                lines = [line.strip() for line in file]

            modified_lines = process_music_list(lines)
            if modified_lines != lines:
                write_and_replace(file_path, modified_lines)
    finally:
        if args.selenium:
            web.quit_selenium(args)
