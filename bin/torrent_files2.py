#!/usr/bin/env python3
import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import libtorrent as lt


def read_piece_data(ti, piece_index: int, save_dirs: list[Path]):
    """Read piece_index data from files on disk, returning the concatenated bytes."""
    blocks = ti.map_block(piece_index, 0, ti.piece_size(piece_index))
    data = bytearray()
    for b in blocks:
        fs = ti.files()
        file_path = fs.file_path(b.file_index)
        full_path = None
        for d in save_dirs:
            candidate = d / file_path
            if candidate.exists():
                full_path = candidate
                break
        if not full_path:
            return None
        with open(full_path, "rb") as f:
            f.seek(b.offset)
            chunk = f.read(b.size)
            if len(chunk) < b.size:
                return None
            data.extend(chunk)
    return bytes(data)


def check_torrent_progress(ti, save_dirs: list[Path]):
    """Return matched pieces count, total pieces, and missing files."""
    matched_pieces = 0
    total_pieces = ti.num_pieces()
    matched_files = set()
    fs = ti.files()

    for i in range(total_pieces):
        piece_data = read_piece_data(ti, i, save_dirs)
        if not piece_data:
            continue
        piece_hash = hashlib.sha1(piece_data).digest()
        if piece_hash == ti.hash_for_piece(i):
            matched_pieces += 1
            blocks = ti.map_block(i, 0, ti.piece_size(i))
            for b in blocks:
                matched_files.add(fs.file_path(b.file_index))

    all_files = {fs.file_path(i) for i in range(ti.num_files())}
    missing = all_files - matched_files
    pct = (matched_pieces / total_pieces) * 100 if total_pieces else 0
    return matched_pieces, total_pieces, pct, missing


def main():
    parser = argparse.ArgumentParser(
        description="Multi-file torrent matcher using libtorrent 2.x with size-first optimization"
    )
    parser.add_argument("torrent_dir", type=Path)
    parser.add_argument("search_dirs", nargs="+", type=Path)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--min-pieces", type=int, default=1)
    args = parser.parse_args()

    limits = {
        "max_buffer_size": 55_000_000,  # max .torrent size in bytes
        "max_pieces": 2_000_000,
        "max_decode_tokens": 5_000_000,  # max tokens in bdecode
    }

    # Load torrents
    torrents = []
    size_index = {}  # size → list of (ti, torfile)
    for torfile in args.torrent_dir.glob("*.torrent"):
        try:
            ti = lt.torrent_info(str(torfile), limits)
            torrents.append((ti, torfile))
            fs = ti.files()
            for i in range(ti.num_files()):
                size = fs.file_size(i)
                size_index.setdefault(size, []).append((ti, torfile))
        except Exception as e:
            print(f"[ERROR] {torfile}: {e}")

    # Collect all files on disk
    file_sizes = {}
    for d in args.search_dirs:
        for f in d.rglob("*"):
            if f.is_file():
                file_sizes.setdefault(f.stat().st_size, []).append(f)

    # Identify candidate torrents with at least one matching file size
    candidate_torrents = set()
    for size, _files in file_sizes.items():
        if size in size_index:
            for ti, torfile in size_index[size]:
                candidate_torrents.add((ti, torfile))

    # Process candidate torrents in threads
    summary = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(check_torrent_progress, ti, args.search_dirs): torfile
            for ti, torfile in candidate_torrents
        }
        for future in as_completed(futures):
            torfile = futures[future]
            try:
                matched, total, pct, missing = future.result()
                if matched >= args.min_pieces:
                    summary.append((pct, torfile, matched, total, missing))
            except Exception as e:
                print(f"[ERROR] {torfile}: {e}")

    summary.sort(reverse=True, key=lambda x: x[0])
    print("\n=== Torrent Progress ===")
    for pct, torfile, matched, total, missing in summary:
        missing_info = ""
        if missing:
            if len(missing) == 1:
                missing_info = f" [{next(iter(missing))} missing]"
            else:
                missing_info = f" [{len(missing)} files missing]"
        print(f"{torfile.name} {matched}/{total} pieces ({pct:.1f}%) {missing_info}")

    print(f"\n{len(summary)} torrents with at least one matching piece.")


if __name__ == "__main__":
    main()
