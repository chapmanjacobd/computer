#!/usr/bin/env python3
import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import libtorrent as lt


def piecewise_hash(file_path: Path, piece_length: int, piece_hashes: list[bytes]):
    """Return number of matching pieces out of total for a file against torrent piece hashes."""
    matches = 0
    total = len(piece_hashes)
    with open(file_path, "rb") as f:
        for expected_hash in piece_hashes:
            data = f.read(piece_length)
            if not data:
                break
            actual = hashlib.sha1(data).digest()
            if actual == expected_hash:
                matches += 1
    return matches, total


def check_file_against_torrent(file_path: Path, ti: lt.torrent_info, f, min_pieces: int):
    """Check if a candidate file matches a given torrent file entry."""
    piece_length = ti.piece_length()
    piece_start = f.offset // piece_length
    piece_end = (f.offset + f.size + piece_length - 1) // piece_length

    piece_hashes = [ti.hash_for_piece(i) for i in range(piece_start, piece_end)]

    matches, total = piecewise_hash(file_path, piece_length, piece_hashes)
    if matches >= min_pieces:
        pct = (matches / total) * 100 if total else 0
        return f, matches, total, pct
    return None


def main():
    parser = argparse.ArgumentParser(description="Match files against torrents by size + piece-hash (libtorrent).")
    parser.add_argument("torrent_dir", type=Path, help="Directory of .torrent files")
    parser.add_argument("search_dirs", nargs="+", type=Path, help="Directories to scan")
    parser.add_argument("--threads", type=int, default=6, help="Number of hashing threads")
    parser.add_argument(
        "--min-pieces",
        type=int,
        default=1,
        help="Minimum number of pieces that must match (default=1)",
    )
    args = parser.parse_args()

    # Load torrents
    torrents = []
    for torfile in args.torrent_dir.glob("*.torrent"):
        try:
            ti = lt.torrent_info(str(torfile))
            torrents.append((ti, torfile))
        except Exception as e:
            print(f"[ERROR] {torfile}: {e}")

    # Index torrent files by size
    size_index = {}
    for ti, torfile in torrents:
        for f in ti.files():
            size_index.setdefault(f.size, []).append((ti, torfile, f))

    # progress: infohash → [matched_pieces, total_pieces, torrent_info, torfile, set(matched_file_paths)]
    torrent_progress = {ti.info_hash().to_string(): [0, 0, ti, torfile, set()] for ti, torfile in torrents}

    # Collect candidate files
    candidates = []
    for d in args.search_dirs:
        for f in d.rglob("*"):
            if f.is_file():
                candidates.append(f)

    # Dispatch work
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {}
        for f in candidates:
            size = f.stat().st_size
            if size not in size_index:
                continue  # no possible torrent matches
            for ti, torfile, tf in size_index[size]:
                futures[executor.submit(check_file_against_torrent, f, ti, tf, args.min_pieces)] = (f, ti)

        for future in as_completed(futures):
            f, ti = futures[future]
            try:
                result = future.result()
            except Exception as e:
                print(f"[ERROR] {f} vs {ti.name()}: {e}")
                continue

            if result:
                tf, matches, total, pct = result
                print(f"[MATCH] {f} ↔ {ti.name()}/{tf.path} " f"{matches}/{total} pieces ({pct:.1f}%)")
                prog = torrent_progress[ti.info_hash().to_string()]
                prog[0] += matches
                prog[1] += total
                prog[4].add(tf.path)  # track matched file paths

    # Torrent-level progress
    summary = []
    for infohash, (matched, total, ti, torfile, matched_files) in torrent_progress.items():
        if total > 0:
            pct = (matched / total) * 100
            all_files = {f.path for f in ti.files()}
            missing = all_files - matched_files
            summary.append((pct, ti, torfile, missing))

    summary.sort(reverse=True, key=lambda x: x[0])
    print("\n=== Torrent Progress ===")
    for pct, ti, torfile, missing in summary:
        missing_info = ""
        if missing:
            if len(missing) == 1:
                missing_info = f" [{next(iter(missing))} missing]"
            else:
                missing_info = f" [{len(missing)} files missing]"
        print(f"{torfile.name} ({ti.name()}): {pct:.1f}%{missing_info}")

    print(f"\n{len(summary)} torrents with at least one matching file.")


if __name__ == "__main__":
    main()
