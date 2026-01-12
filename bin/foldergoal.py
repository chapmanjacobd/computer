#!/usr/bin/env python3
"""
foldergoal.py - Manage whole folders between backing and staging directories based on constraints.
"""

import argparse
import sys
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from library.utils import arggroups, consts, nums, processes, shell_utils, strings
from library.utils.log_utils import log
from library.utils.processes import FFProbe


@dataclass
class FileInfo:
    """Store file metadata."""

    path: Path
    size: int
    duration: Optional[float]
    bitrate: Optional[float]


@dataclass
class FolderInfo:
    """Store folder metadata."""

    path: Path
    size: int
    duration: float
    file_count: int
    files: List[FileInfo]


def parse_constraint(human_parser: Callable, constraint: str) -> tuple:
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

    files, _filtered_files, _folders = shell_utils.rglob(
        directory, consts.VIDEO_EXTENSIONS | consts.AUDIO_ONLY_EXTENSIONS
    )
    files = [Path(s) for s in files]
    with ThreadPoolExecutor() as executor:
        media = list(executor.map(get_file_info, files))

    return media


def group_by_folders(files: List[FileInfo], base_dir: Path) -> List[FolderInfo]:
    """Group files by their direct parent folder under base_dir."""
    folder_files: Dict[Path, List[FileInfo]] = defaultdict(list)

    for file_info in files:
        # Find the direct child folder of base_dir
        relative = file_info.path.relative_to(base_dir)
        if len(relative.parts) > 1:
            # File is in a subfolder
            folder = base_dir / relative.parts[0]
        else:
            # File is directly in base_dir (shouldn't happen with media typically)
            folder = base_dir

        folder_files[folder].append(file_info)

    # Create FolderInfo objects
    folders = []
    for folder_path, folder_file_list in folder_files.items():
        total_size = sum(f.size for f in folder_file_list)
        total_duration = sum(f.duration or 0 for f in folder_file_list)

        folders.append(
            FolderInfo(
                path=folder_path,
                size=total_size,
                duration=total_duration,
                file_count=len(folder_file_list),
                files=folder_file_list,
            )
        )

    return folders


def sort_folders(folders: List[FolderInfo], sort_by: str, reverse: bool = True) -> List[FolderInfo]:
    if sort_by == 'bitrate':
        # Calculate average bitrate for folder
        def avg_bitrate(folder: FolderInfo) -> float:
            if folder.duration > 0:
                return (folder.size * 8) / folder.duration
            return 0

        return sorted(folders, key=avg_bitrate, reverse=reverse)
    elif sort_by == 'size':
        return sorted(folders, key=lambda f: f.size, reverse=reverse)
    elif sort_by == 'duration':
        return sorted(folders, key=lambda f: f.duration, reverse=reverse)
    elif sort_by == 'name':
        return sorted(folders, key=lambda f: f.path.name, reverse=reverse)
    else:
        return folders


def move_folder(src_folder: Path, dest_folder: Path) -> None:
    """Move entire folder from src to dest."""
    dest_folder.parent.mkdir(parents=True, exist_ok=True)

    # Use cp -rp to preserve metadata and copy recursively
    processes.cmd("cp", "-rp", src_folder, dest_folder.parent, journald=False)
    # Remove source folder after successful copy
    processes.cmd("rm", "-rf", src_folder, journald=False)


def main():
    parser = argparse.ArgumentParser(
        description="Manage whole folders between backing and staging directories based on constraints.",
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
        help="Sort criterion for folder selection (default: bitrate)",
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

    # Scan staging directory
    staging_files = scan_directory(args.staging_dir)
    staging_folders = group_by_folders(staging_files, args.staging_dir)

    staging_size = sum(f.size for f in staging_files)
    staging_duration = sum(f.duration or 0 for f in staging_files)

    print(
        f"Staging: {len(staging_folders)} folders, {len(staging_files)} files, {strings.file_size(staging_size)}, {strings.duration_short(staging_duration)}"
    )

    # Determine if we need to add or remove folders
    need_size = size_min - staging_size if staging_size < size_min else 0
    excess_size = staging_size - size_max if staging_size > size_max else 0

    need_duration = duration_min - staging_duration if staging_duration < duration_min else 0
    excess_duration = staging_duration - duration_max if staging_duration > duration_max else 0

    if excess_size > 0 or excess_duration > 0:
        if excess_size > 0:
            print(f"  - Size: -{strings.file_size(excess_size)}")
        if excess_duration > 0:
            print(f"  - Duration: -{strings.duration_short(excess_duration)}")

        sorted_folders = sort_folders(staging_folders, args.sort, reverse=not args.reverse)

        removed_size = 0
        removed_duration = 0
        removed_folders = 0
        for folder_info in sorted_folders:
            if removed_size >= excess_size and removed_duration >= excess_duration:
                break

            src = folder_info.path
            dest = args.backing_dir / src.relative_to(args.staging_dir)
            log.info(
                "%s (%d files, %s, %s)",
                src.name,
                folder_info.file_count,
                strings.file_size(folder_info.size),
                strings.duration_short(folder_info.duration),
            )
            log.info("--> %s", dest)

            if not args.simulate:
                move_folder(src, dest)

            removed_size += folder_info.size
            removed_duration += folder_info.duration
            removed_folders += 1

        print(
            f"\nRemoved from staging: {removed_folders} folders, {strings.file_size(removed_size)}, {strings.duration_short(removed_duration)}"
        )

    elif need_size > 0 or need_duration > 0:
        if need_size > 0:
            print(f"  - Size: +{strings.file_size(need_size)}")
        if need_duration > 0:
            print(f"  - Duration: +{strings.duration_short(need_duration)}")

        print(f"\nScanning backing directory: {args.backing_dir}")
        backing_files = scan_directory(args.backing_dir)
        backing_folders = group_by_folders(backing_files, args.backing_dir)
        print(f"Backing: {len(backing_folders)} folders, {len(backing_files)} files")

        sorted_folders = sort_folders(backing_folders, args.sort, reverse=args.reverse)

        added_size = 0
        added_duration = 0
        added_folders = 0
        for folder_info in sorted_folders:
            if added_size >= need_size and added_duration >= need_duration:
                break

            src = folder_info.path
            dest = args.staging_dir / src.relative_to(args.backing_dir)
            log.info(
                "%s (%d files, %s, %s)",
                src.name,
                folder_info.file_count,
                strings.file_size(folder_info.size),
                strings.duration_short(folder_info.duration),
            )
            log.info("--> %s", dest)

            if not args.simulate:
                move_folder(src, dest)

            added_size += folder_info.size
            added_duration += folder_info.duration
            added_folders += 1

        print(
            f"\nAdded to staging: {added_folders} folders, {strings.file_size(added_size)}, {strings.duration_short(added_duration)}"
        )

    else:
        print("\nStaging directory is within goal constraints. No changes needed.")


if __name__ == "__main__":
    main()
