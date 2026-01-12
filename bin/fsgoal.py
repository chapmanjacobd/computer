#!/usr/bin/env python3
"""
fsgoal.py - Manage files between backing and staging directories based on constraints.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from library.utils import arggroups, consts, nums, shell_utils, strings
from library.utils import processes
from library.utils.log_utils import log
from library.utils.processes import FFProbe


@dataclass
class FileInfo:
    """Store file metadata."""

    path: Path
    size: int
    duration: Optional[float]
    bitrate: Optional[float]


def parse_constraint(human_parser: Callable[[str], float], constraint: str):
    """
    Parse constraint string to min/max values.
    Examples:
    - "6" -> exactly 6 MB
    - "-6" -> less than 6 MB
    - "+6" -> more than 6 MB
    - "6%10" -> 6 MB ±10%
    """
    constraint = constraint.strip()

    # Check for percentage tolerance
    if '%' in constraint:
        parts = constraint.split('%')
        base_str = parts[0]
        tolerance = float(parts[1])

        # Handle +/- prefix
        if base_str.startswith('+'):
            base = human_parser(base_str[1:])
            min_val = base
            max_val = base * (1 + tolerance / 100)
        elif base_str.startswith('-'):
            base = human_parser(base_str[1:])
            min_val = 0
            max_val = base * (1 + tolerance / 100)
        else:
            base = human_parser(base_str)
            min_val = base * (1 - tolerance / 100)
            max_val = base * (1 + tolerance / 100)

        return (min_val, max_val)

    # Handle +/- prefix
    if constraint.startswith('+'):
        value = human_parser(constraint[1:])
        return (value, float('inf'))
    elif constraint.startswith('-'):
        value = human_parser(constraint[1:])
        return (0, value)
    else:
        value = human_parser(constraint)
        return (value, value)


def combine_constraints(constraints: List[str], human_parser) -> Tuple[float, float]:
    """Combine multiple constraints into final min/max range."""
    min_val = 0
    max_val = float('inf')

    for constraint in constraints:
        c_min, c_max = parse_constraint(human_parser, constraint)
        min_val = max(min_val, c_min)
        max_val = min(max_val, c_max)

    return (min_val, max_val)


def get_file_info(file_path: Path) -> FileInfo:
    size = file_path.stat().st_size
    duration = None
    bitrate = None

    try:
        probe = FFProbe(str(file_path))
        duration = probe.duration

        if duration and duration > 0:
            # Bitrate in bits per second
            bitrate = (size * 8) / duration
    except Exception as e:
        log.warning("Could not probe %s: %s", file_path, e)

    return FileInfo(path=file_path, size=size, duration=duration, bitrate=bitrate)


def scan_directory(directory: Path) -> List[FileInfo]:
    if not directory.exists():
        return []

    files, _filtered_files, _folders = shell_utils.rglob(directory, consts.VIDEO_EXTENSIONS | consts.AUDIO_ONLY_EXTENSIONS)
    files = [Path(s) for s in files]
    with ThreadPoolExecutor() as executor:
        media = list(executor.map(get_file_info, files))

    return media


def sort_files(files: List[FileInfo], sort_by: str, reverse: bool = True) -> List[FileInfo]:
    if sort_by == 'bitrate':
        # Put files without bitrate at the end
        return sorted(files, key=lambda f: (f.bitrate is not None, f.bitrate or 0), reverse=reverse)
    elif sort_by == 'size':
        return sorted(files, key=lambda f: f.size, reverse=reverse)
    elif sort_by == 'duration':
        return sorted(files, key=lambda f: (f.duration is not None, f.duration or 0), reverse=reverse)
    elif sort_by == 'name':
        return sorted(files, key=lambda f: f.path.name, reverse=reverse)
    else:
        return files


def move_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    processes.cmd("cp", "-p", src, dest, journald=False)
    os.remove(src)


def main():
    parser = argparse.ArgumentParser(
        description="Manage files between backing and staging directories based on constraints.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--size",
        "--sizes",
        "-S",
        action="append",
        dest="sizes",
        help="""Constrain total size (uses the same syntax as fd-find)
-S 6           # 6 MB exactly (not likely)
-S-6           # less than 6 MB
-S+6           # more than 6 MB
-S 6%%10       # 6 MB ±10 percent (between 5 and 7 MB)
-S+5GB -S-7GB  # between 5 and 7 GB""",
    )
    parser.add_argument(
        "--duration",
        "-d",
        action="append",
        help="""Constrain total duration (same syntax as size)
-d 2h          # 2 hours exactly
-d-30m         # less than 30 minutes
-d+1h -d-2h    # between 1 and 2 hours""",
    )
    parser.add_argument(
        "--sort",
        "-s",
        choices=['bitrate', 'size', 'duration', 'name'],
        default='bitrate',
        help="Sort criterion for file selection (default: bitrate)",
    )
    parser.add_argument(
        "-u",
        "--reverse",
        action="store_false",
        dest="reverse",
        help="Reverse sort order (prioritize low values instead of high)",
    )
    arggroups.debug(parser)

    parser.add_argument("backing_dir", type=Path, help="Backing directory")
    parser.add_argument("staging_dir", type=Path, help="Staging directory")
    args = parser.parse_args()

    if not args.backing_dir.exists():
        print(f"Error: Backing directory does not exist: {args.backing_dir}", file=sys.stderr)
        sys.exit(1)

    args.staging_dir.mkdir(parents=True, exist_ok=True)

    size_min, size_max = (0, float('inf'))
    duration_min, duration_max = (0, float('inf'))

    if args.sizes:
        size_min, size_max = combine_constraints(args.sizes, nums.human_to_bytes)
        log.info(f"Size goal: {strings.file_size(size_min)} - {strings.file_size(size_max)}")

    if args.duration:
        duration_min, duration_max = combine_constraints(args.duration, nums.human_to_seconds)
        log.info(f"Duration goal: {strings.duration_short(duration_min)} - {strings.duration_short(duration_max)}")

    staging_files = scan_directory(args.staging_dir)

    staging_size = sum(f.size for f in staging_files)
    staging_duration = sum(f.duration or 0 for f in staging_files)

    print(f"Staging: {len(staging_files)} files, {strings.file_size(staging_size)}, {strings.duration_short(staging_duration)}")

    # Determine if we need to add or remove files
    need_size = size_min - staging_size if staging_size < size_min else 0
    excess_size = staging_size - size_max if staging_size > size_max else 0

    need_duration = duration_min - staging_duration if staging_duration < duration_min else 0
    excess_duration = staging_duration - duration_max if staging_duration > duration_max else 0

    if excess_size > 0 or excess_duration > 0:
        if excess_size > 0:
            print(f"  - Size: -{strings.file_size(excess_size)}")
        if excess_duration > 0:
            print(f"  - Duration: -{strings.duration_short(excess_duration)}")

        sorted_files = sort_files(staging_files, args.sort, reverse=not args.reverse)

        removed_size = 0
        removed_duration = 0
        for file_info in sorted_files:
            if removed_size >= excess_size and removed_duration >= excess_duration:
                break

            if not file_info.duration:
                continue

            new_staging_size = staging_size - (removed_size + file_info.size)
            new_staging_duration = staging_duration - (removed_duration + file_info.duration)
            if new_staging_size < size_min or new_staging_duration < duration_min:
                continue

            src = file_info.path
            dest = args.backing_dir / src.relative_to(args.staging_dir)
            log.info("%s", src)
            log.info("--> %s", dest)
            if not args.simulate:
                move_file(src, dest)

            removed_size += file_info.size
            removed_duration += file_info.duration or 0

        print(f"\nRemoved from staging: {strings.file_size(removed_size)}, {strings.duration_short(removed_duration)}")

    elif need_size > 0 or need_duration > 0:
        if need_size > 0:
            print(f"  - Size: +{strings.file_size(need_size)}")
        if need_duration > 0:
            print(f"  - Duration: +{strings.duration_short(need_duration)}")

        print(f"\nScanning backing directory: {args.backing_dir}")
        backing_files = scan_directory(args.backing_dir)
        print(f"Backing: {len(backing_files)} files")

        sorted_files = sort_files(backing_files, args.sort, reverse=args.reverse)

        added_size = 0
        added_duration = 0
        for file_info in sorted_files:
            if added_size >= need_size and added_duration >= need_duration:
                break

            if not file_info.duration:
                continue

            new_staging_size = staging_size + added_size + file_info.size
            new_staging_duration = staging_duration + added_duration + file_info.duration
            if new_staging_size > size_max or new_staging_duration > duration_max:
                continue

            src = file_info.path
            dest = args.staging_dir / src.relative_to(args.backing_dir)
            log.info("%s", src)
            log.info("--> %s", dest)
            if not args.simulate:
                move_file(src, dest)

            added_size += file_info.size
            added_duration += file_info.duration or 0

        print(f"\nAdded to staging: {strings.file_size(added_size)}, {strings.duration_short(added_duration)}")

    else:
        print("\nStaging directory is within goal constraints. No changes needed.")


if __name__ == "__main__":
    main()
