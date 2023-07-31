#!/usr/bin/python3

import argparse
import difflib
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from screeninfo import get_monitors


def read_file(file_path):
    backup_filename = file_path + ".bak"
    if not os.path.exists(backup_filename):
        try:
            shutil.copy2(file_path, backup_filename)
        except Exception as e:
            print(f"Failed to create backup file: {e}")

    with open(file_path, "r") as file:
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
    groups = group_content.split("\n")
    if len(groups) < 2:
        return
    for match in groups:
        if match == '':
            continue
        size_str = match.split(" - ")[-1]
        size_value, size_unit = float(size_str.split()[0]), size_str.split()[1]
        if size_unit == "GiB":
            size_value *= 1024
        elif size_unit == "KiB":
            size_value /= 1024
        paths_and_sizes.append({"path": ' - '.join(match.split(" - ")[:-1]), "size_mb": size_value})
    return paths_and_sizes


def truncate_file_before_match(filename, match_string):
    with open(filename, 'r') as file:
        lines = file.readlines()
    matching_lines = [i for i, line in enumerate(lines) if match_string in line]

    if len(matching_lines) == 1:
        line_index = matching_lines[0]
        with open(filename, 'w') as file:
            file.write("".join(lines[line_index - 1 :]))
        print(f"File truncated before the line containing: '{match_string}'")
        print(f"{len(lines[line_index - 1 :])} left to check")
    elif len(matching_lines) == 0:
        print(f"Match not found in the file: '{match_string}'")
    else:
        print(f"Multiple matches found in the file for: '{match_string}'")


def launch_mpv_compare(left_side, right_side):
    # Get the size of the first connected display
    monitors = get_monitors()
    if not monitors:
        print("No connected displays found.")
        return

    display_width = monitors[0].width
    mpv_width = display_width // 2

    left_mpv_process = subprocess.Popen(
        [
            "mpv",
            left_side,
            f"--geometry={mpv_width}x{monitors[0].height}+0+0",
            '--save-position-on-quit=no',
            '--no-resume-playback',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    right_mpv_process = subprocess.Popen(
        [
            "mpv",
            right_side,
            f"--geometry={mpv_width}x{monitors[0].height}+{mpv_width}+0",
            '--save-position-on-quit=no',
            '--no-resume-playback',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Monitor the processes and terminate the other one when one finishes
    while True:
        if left_mpv_process.poll() is not None or right_mpv_process.poll() is not None:
            break
        time.sleep(0.1)

    # Terminate the other process
    if left_mpv_process.poll() is None:
        left_mpv_process.terminate()
    if right_mpv_process.poll() is None:
        right_mpv_process.terminate()


def group_and_delete(args, groups):
    for group_content in groups:
        if group_content == "":
            continue

        group = extract_paths_and_sizes(group_content)
        if group is None:
            continue
        group.sort(key=lambda x: x["size_mb"], reverse=True)
        largest_path = group[0]["path"]

        if os.path.exists(largest_path):
            print(largest_path)

            delete_largest_path = False
            for d in group[1:]:
                path = d["path"]
                if os.path.exists(path):
                    similar_ratio = difflib.SequenceMatcher(
                        None, os.path.basename(largest_path), os.path.basename(path)
                    ).ratio()
                    if similar_ratio > 0.7 or any(s in largest_path and s in path for s in ['Goldmines_Bollywood']):
                        Path(path).unlink(missing_ok=True)
                        print(f"{path}: Deleted")
                    else:
                        print(path)
                        if not any([args.all_keep, args.all_left,args.all_right,args.all_delete]):
                            launch_mpv_compare(largest_path, path)
                        while True:
                            user_input=''
                            if not any([args.all_keep, args.all_left,args.all_right,args.all_delete]):
                                user_input = (
                                    input(
                                        "Names are pretty different. Keep which files? (l Left/r Right/k Keep both/d Delete both) [default: l]: "
                                    )
                                    .strip()
                                    .lower()
                                )
                            if args.all_keep or user_input in ("k", "b", "both"):
                                break
                            elif args.all_left or user_input in ("l", "left", ""):
                                Path(path).unlink(missing_ok=True)
                                print(f"{path}: Deleted")
                                break
                            elif args.all_right or user_input in ("r", "right", ""):
                                largest_path, path = path, largest_path
                                Path(path).unlink(missing_ok=True)
                                print(f"{path}: Deleted")
                                break
                            elif args.all_delete or user_input in ("d"):
                                Path(path).unlink(missing_ok=True)
                                print(f"{path}: Deleted")
                                delete_largest_path = True
                                break
                            elif user_input in ("q"):
                                truncate_file_before_match(args.file_path, largest_path)
                                if delete_largest_path:
                                    Path(largest_path).unlink(missing_ok=True)
                                sys.exit(0)
                            else:
                                print("Invalid input. Please type 'y', 'n', or nothing and enter")
                else:
                    print(f"{path}: not found")
            if delete_largest_path:
                Path(largest_path).unlink(missing_ok=True)
                print(f"{largest_path}: Deleted")
        else:
            print(f"Original not found: {largest_path}")

        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup duplicate files based on their sizes.")
    parser.add_argument("file_path", help="Path to the text file containing the file list.")
    parser.add_argument("--all-keep", action='store_true')
    parser.add_argument("--all-left", action='store_true')
    parser.add_argument("--all-right", action='store_true')
    parser.add_argument("--all-delete", action='store_true')
    args = parser.parse_args()

    content = read_file(args.file_path)
    groups = extract_groups(content)
    group_and_delete(args, groups)
