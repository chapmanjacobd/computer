#!/usr/bin/python3
import argparse
import os
import sqlite3
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Optional

from library.utils import arggroups, argparse_utils, devices, strings, nums
from library.utils.log_utils import log


@dataclass
class MountInfo:
    path: str
    total_size: int
    free_space: int


@dataclass
class MediaFile:
    path: str
    size: int
    duration: float
    bitrate: float
    db_path: str
    mount: MountInfo
    is_high_br: bool = False
    mismatch_score: float = 0.0


def get_mounts(args) -> List[MountInfo]:
    mounts = []

    if args.mounts:
        for mountpoint in args.mounts:
            try:
                # Use stat -f to get filesystem info
                result = subprocess.run(
                    ['stat', '-f', '-c', '%S %a %b', mountpoint], capture_output=True, text=True, check=True
                )
                block_size, available_blocks, total_blocks = map(int, result.stdout.strip().split())

                total_size = block_size * total_blocks
                free_space = block_size * available_blocks

                mounts.append(MountInfo(path=os.path.abspath(mountpoint), total_size=total_size, free_space=free_space))
            except (PermissionError, OSError, subprocess.CalledProcessError, ValueError):
                if args.exists:
                    continue
                else:
                    mounts.append(MountInfo(path=mountpoint, total_size=nums.human_to_bytes("3TB"), free_space=0))
    else:
        import psutil

        for part in psutil.disk_partitions():
            mountpoint = part.mountpoint
            if mountpoint in [os.sep, "/var", "/etc", "/usr"] or mountpoint.startswith(("/boot", "/sysroot")):
                continue
            if mountpoint in ("/var/home", "/home"):
                mountpoint = os.path.expanduser('~')

            try:
                usage = psutil.disk_usage(mountpoint)
                mounts.append(
                    MountInfo(path=os.path.abspath(mountpoint), total_size=usage.total, free_space=usage.free)
                )
            except (PermissionError, OSError):
                continue

    return mounts


def find_mount(file_path: str, mounts: List[MountInfo]) -> Optional[MountInfo]:
    file_path = os.path.abspath(file_path)
    best_match = None
    for m in mounts:
        if file_path == m.path or file_path.startswith(m.path + os.sep):
            if not best_match or len(m.path) > len(best_match.path):
                best_match = m
    return best_match


def query_databases(args: argparse.Namespace, mounts: List[MountInfo]) -> List[MediaFile]:
    files = []
    for db_path in args.paths:
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    f"""SELECT path, size, duration
                    FROM media
                    WHERE time_deleted = 0
                        AND duration > 0
                        AND ((path NOT LIKE '%/seeding/%' AND path NOT LIKE '%/downloading/%') OR (path LIKE '%/process%'))
                        AND video_count {'= 0' if args.audio else '> 0'}
                    """
                )
                for row in cursor:
                    m = find_mount(row['path'], mounts)
                    if m:
                        br = (row['size'] * 8) / row['duration']
                        files.append(
                            MediaFile(
                                path=row['path'],
                                size=row['size'],
                                duration=row['duration'],
                                bitrate=br,
                                db_path=db_path,
                                mount=m,
                            )
                        )
        except Exception as e:
            log.error(f"Error reading {db_path}: {e}")
    return files


def move_file(src, dst) -> bool:
    if not os.path.exists(src):
        return False

    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
    except OSError:
        log.error(f"Failed to mkdir for {dst}")
        return False

    try:
        log.info("%s", src)
        log.info("--> %s", dst)

        subprocess.run(["cp", "--sparse=auto", "-p", src, dst], check=True, capture_output=True)
        os.remove(src)
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to move {src}: {e.stderr.decode()}")
        return False


def plan_and_execute(args, files: List[MediaFile], mounts: List[MountInfo]):
    min_free = 50 * 1024 * 1024 * 1024
    planned_moves = []

    # Calculate Mismatch Scores
    # High Score = High Bitrate on Small Drive OR Low Bitrate on Large Drive
    avg_br = sum(f.bitrate for f in files) / len(files)
    print("Avg. bitrate:", strings.file_size(avg_br) + '/s')
    for f in files:
        f.is_high_br = f.bitrate > avg_br
        if f.is_high_br:
            if f.path.endswith((".mka", ".av1.mkv")):
                f.is_high_br = False
        else:
            if f.path.lower().endswith((".vob", ".iso", ".img")):
                f.is_high_br = True

        gb_size = f.mount.total_size / 1e9
        f.mismatch_score = f.bitrate / gb_size if f.is_high_br else gb_size / (f.bitrate + 1)

    # Sort by extreme mismatches first
    files.sort(key=lambda x: x.mismatch_score, reverse=True)
    files = files[: (len(files) * 2) // 3]  # only move extreme cases

    # Simulation/Planning Loop
    # We iterate multiple times to allow space to "open up" from previous moves
    work_queue = files.copy()
    iteration = 0
    while iteration < 3 and work_queue:
        still_waiting = []
        for f in work_queue:
            best_target = None

            # Sort targets based on file type
            if f.is_high_br:
                # Want largest available drive that is bigger than current
                targets = sorted(
                    [m for m in mounts if m.total_size > (f.mount.total_size * 2)],
                    key=lambda x: x.total_size,
                    reverse=True,
                )
            else:
                # Want smallest available drive that is smaller than current
                targets = sorted(
                    [m for m in mounts if m.total_size < (f.mount.total_size / 2)], key=lambda x: x.total_size
                )

            for target in targets:
                if target.free_space > (f.size + min_free):
                    best_target = target
                    break

            if best_target:
                if args.exists and not os.path.exists(f.path):
                    continue

                planned_moves.append((f, best_target))
                best_target.free_space -= f.size
                f.mount.free_space += f.size  # Simulate space recovery
            else:
                still_waiting.append(f)

        print(
            "Planning iteration",
            iteration,
            "planned",
            len(planned_moves),
            "; still waiting for",
            len(still_waiting),
            "files",
        )
        work_queue = still_waiting
        iteration += 1

    # Print Plan
    # for f, target in planned_moves:
    #     label = "HI" if f.is_high_br else "LO"
    #     print(
    #         f"[{label}] {os.path.basename(f.path)[:40]:<40} | "
    #         f"{f.mount.total_size // 10**12}TB -> {target.total_size // 10**12}TB"
    #     )

    # Calculate Totals
    total_bytes = sum(f.size for f, _ in planned_moves)
    high_br_bytes = sum(f.size for f, _ in planned_moves if f.is_high_br)
    low_br_bytes = sum(f.size for f, _ in planned_moves if not f.is_high_br)

    print(f"\n--- Rebalance Plan ---")
    print(f"Total Moves:     {len(planned_moves)} ({total_bytes / 1024**3:.2f} GB)")
    print(f"    High-BR:     {sum(1 for f, _ in planned_moves if f.is_high_br)} ({high_br_bytes / 1024**3:.2f} GB)")
    print(f"     Low-BR:     {sum(1 for f, _ in planned_moves if not f.is_high_br)} ({low_br_bytes / 1024**3:.2f} GB)")
    print("-" * 22)

    by_mount = defaultdict(lambda: {"count": 0, "size": 0})
    for f, target in planned_moves:
        key = (f.mount.path, target.path)
        by_mount[key]["count"] += 1
        by_mount[key]["size"] += f.size
    for (src, dst), data in by_mount.items():
        print(f"{src} -> {dst} | {data['count']} files ({strings.file_size(data['size'])})")

    if planned_moves and devices.confirm("\nExecute moves?"):
        for f, target in planned_moves:
            rel_path = os.path.relpath(f.path, f.mount.path)
            dest_path = os.path.join(target.path, rel_path)
            move_file(f.path, dest_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", action="store_true")
    parser.add_argument("--exists", action="store_true")
    parser.add_argument("--mounts", "-m", action=argparse_utils.ArgparseList, help="Mount points to check (optional)")
    arggroups.debug(parser)

    parser.add_argument('paths', nargs='+', help='SQLite database paths')
    args = parser.parse_args()

    mounts = get_mounts(args)
    all_files = query_databases(args, mounts)

    if all_files:
        plan_and_execute(args, all_files, mounts)


if __name__ == "__main__":
    main()
