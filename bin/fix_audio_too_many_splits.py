#!/usr/bin/env python3

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from library.utils import arggroups, processes
from library.utils.log_utils import log
from natsort import natsorted


def group_files_by_prefix(directory_path):
    prefix_groups = defaultdict(list)
    regex = re.compile(r'^(.*)\.\d{2,5}\.(mka|opus)$')
    for filename in os.listdir(directory_path):
        match = regex.match(filename)
        if match:
            prefix = match.group(1)
            filepath = os.path.join(directory_path, filename)
            prefix_groups[prefix].append(filepath)

    for prefix in prefix_groups:
        yield prefix_groups[prefix]


def create_combined_file(file_list, output_dir, start_file):
    output_filename_base = os.path.splitext(os.path.basename(start_file))[0]
    output_format = os.path.splitext(os.path.basename(start_file))[1][1:]
    output_filename = f"{output_filename_base}_combined.temp.{output_format}"
    temp_filepath = os.path.join(output_dir, output_filename)
    output_filepath = os.path.join(output_dir, os.path.basename(start_file))

    concat_list_path = os.path.join(output_dir, "concat_list_temp.txt")
    with open(concat_list_path, 'w') as f:
        for file_path_to_concat in file_list:
            quoted_path = shlex.quote(file_path_to_concat)
            f.write(f"file {quoted_path}\n")

    log.info(
        """%s
##> %s""",
        '\n  '.join(file_list),
        start_file,
    )

    command = [
        'ffmpeg',
        '-nostdin',
        "-hide_banner",
        "-nostats",
        "-xerror",
        "-v",
        "16",
        "-err_detect",
        "explode",
        '-y',
        '-safe',
        '0',
        '-f',
        'concat',
        '-i',
        concat_list_path,
        "-af",
        "asetpts=STARTPTS+N",
        temp_filepath,
    ]
    r = subprocess.run(command, capture_output=True)
    os.unlink(concat_list_path)

    if r.returncode == 0:
        shutil.move(temp_filepath, output_filepath)
    elif "Error during demuxing: Invalid data found when processing input" in r.stderr.decode('utf-8'):
        log.info('Error during demuxing. Skipping...')
        Path(temp_filepath).unlink(missing_ok=True)
        return
    else:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        r.check_returncode()

    return output_filepath


def unlink_merged_files(file_list):
    assert os.path.exists(file_list[0])

    for filepath in file_list[1:]:
        os.unlink(filepath)


def combine_audio_in_group(file_group, output_dir):
    if not file_group:
        return None

    current_group_files = []
    current_duration = 0
    start_file = None

    for filepath in file_group:
        probe = processes.FFProbe(filepath)
        duration = probe.duration

        if duration is None:
            continue

        if not current_group_files:
            if duration > 140:
                continue
            start_file = filepath
            log.debug('start_file %s', start_file)

        current_group_files.append(filepath)
        current_duration += duration
        log.debug('current_duration %d (%d from %s)', current_duration, duration, filepath)

        if current_duration >= 150:
            if not start_file:
                raise RuntimeError

            output_filepath = create_combined_file(current_group_files, output_dir, start_file)

            if output_filepath:
                unlink_merged_files(current_group_files)
            else:
                log.error(f"Failed to create combined file for group starting with: {start_file}")
            current_group_files = []
            current_duration = 0
            start_file = None

    if current_group_files and len(current_group_files) > 1 and start_file:  # handle remaining files
        output_filepath = create_combined_file(current_group_files, output_dir, start_file)
        if output_filepath:
            unlink_merged_files(current_group_files)
        else:
            log.error(f"Failed to create combined remainder file for group starting with: {start_file}")


def process_directory(directory_path):
    log.info(f"Processing directory: {directory_path}")
    total_files_processed = 0
    for file_group in group_files_by_prefix(directory_path):
        if len(file_group) > 20:
            file_group = natsorted(file_group)
            log.info(f"Found {len(file_group)} matching files in group {file_group[0]}, processing...")
            combine_audio_in_group(file_group, directory_path)
            total_files_processed += len(file_group)
        else:
            log.info(f"Found {len(file_group)} matching files, skipping group {file_group[0]} (< 20)")
    log.info(
        f"Finished processing directory {directory_path}. Total files in processed groups: {total_files_processed}"
    )


def main():
    parser = argparse.ArgumentParser(description="Combine short audio files")
    arggroups.debug(parser)
    parser.add_argument("directories", nargs='+')
    args = parser.parse_args()

    for base_dir in args.directories:
        base_dir = os.path.realpath(base_dir)

        if os.path.isdir(base_dir):
            for root, _, _ in os.walk(base_dir):
                process_directory(root)
        else:
            log.error(f"Error: '{base_dir}' is not a valid directory: {base_dir}")


if __name__ == "__main__":
    main()
