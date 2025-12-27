#!/usr/bin/env python3

import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import libtorrent as lt
from library.utils import arggroups, devices, strings
from library.mediafiles import torrents_start


def piecewise_hash(file_path: Path, piece_length: int, piece_hashes: list[bytes]):
    matches = 0
    total = len(piece_hashes)

    with open(file_path, "rb") as f:
        for expected in piece_hashes:
            data = f.read(piece_length)
            if not data:
                break
            if hashlib.sha1(data).digest() == expected:
                matches += 1

    return matches, total


def check_file_against_torrent(file_path, ti, fs, file_index, min_pieces):
    piece_length = ti.piece_length()

    offset = fs.file_offset(file_index)
    size = fs.file_size(file_index)

    piece_start = offset // piece_length
    piece_end = (offset + size + piece_length - 1) // piece_length

    piece_hashes = [
        ti.hash_for_piece(i)
        for i in range(piece_start, piece_end)
    ]

    matches, total = piecewise_hash(file_path, piece_length, piece_hashes)

    if matches < min_pieces:
        return None

    return {
        "file_index": file_index,
        "matches": matches,
        "total": total,
        "pct": (matches / total) * 100 if total else 0,
        "local_path": file_path,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Add torrents if ≥ threshold already exists locally"
    )
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    parser.add_argument("--threshold", type=float, default=95.0)
    parser.add_argument("torrent_dir", type=Path)
    parser.add_argument("search_dirs", nargs="+", type=Path)

    args = parser.parse_args()

    limits = {
        "max_buffer_size": 55_000_000,
        "max_pieces": 2_000_000,
        "max_decode_tokens": 5_000_000,
    }

    torrents = []
    for torfile in args.torrent_dir.glob("*.torrent"):
        try:
            ti = lt.torrent_info(str(torfile), limits)
            torrents.append({
                "ti": ti,
                "torfile": torfile,
                "fs": ti.files(),
            })
        except Exception as e:
            print(f"[ERROR] {torfile}: {e}")

    print(f"Loaded {len(torrents)} torrents")

    size_index = {}
    for t in torrents:
        ti = t["ti"]
        fs = t["fs"]

        for i in range(ti.num_files()):
            size = fs.file_size(i)
            size_index.setdefault(size, []).append({
                "ti": ti,
                "torfile": t["torfile"],
                "fs": fs,
                "file_index": i,
            })

    progress = {}
    for t in torrents:
        ti = t["ti"]
        infohash = ti.info_hash().to_string()

        progress[infohash] = {
            "matched_size": 0,
            "total_size": ti.total_size(),
            "ti": ti,
            "torfile": t["torfile"],
            "file_map": {},
        }

    candidates = []
    for d in args.search_dirs:
        if not d.exists():
            print(f"[WARNING] Missing directory: {d}")
            continue
        candidates.extend(f for f in d.rglob("*") if f.is_file())

    print(f"Scanning {len(candidates)} files")

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = {}

        for f in candidates:
            size = f.stat().st_size
            for entry in size_index.get(size, []):
                fut = pool.submit(
                    check_file_against_torrent,
                    f,
                    entry["ti"],
                    entry["fs"],
                    entry["file_index"],
                    1,
                )
                futures[fut] = entry

        for fut in as_completed(futures):
            entry = futures[fut]

            try:
                result = fut.result()
            except Exception as e:
                print(f"[ERROR] {e}")
                continue

            if not result:
                continue

            ti = entry["ti"]
            fs = entry["fs"]
            infohash = ti.info_hash().to_string()

            torrent_path = fs.file_path(result["file_index"])
            file_size = fs.file_size(result["file_index"])

            credited = int(
                file_size * (result["matches"] / result["total"])
            ) if result["total"] else 0

            prog = progress[infohash]

            if torrent_path not in prog["file_map"]:
                prog["matched_size"] += credited
                prog["file_map"][torrent_path] = result["local_path"]

    results = []
    for p in progress.values():
        if not p["total_size"]:
            continue

        pct = (p["matched_size"] / p["total_size"]) * 100
        if pct >= args.threshold:
            results.append({
                "pct": pct,
                **p,
            })

    results.sort(key=lambda r: r["pct"], reverse=True)
    print(f"\nFound {len(results)} torrents ≥ {args.threshold}%")

    for r in results:
        print(
            f"\n{r['torfile'].name} ({r['ti'].name()}): "
            f"{r['pct']:.1f}% "
            f"({strings.file_size(r['matched_size'])}/"
            f"{strings.file_size(r['total_size'])})"
        )

    if devices.confirm("Add to qBittorrent?"):
        qbt_client = torrents_start.start_qBittorrent(args)

        for r in results:
            first_path = next(iter(r["file_map"].values()))
            save_path = first_path.parent

            qbt_client.torrents_add(
                torrent_files=open(r["torfile"], "rb"),
                save_path=str(save_path),
                is_paused=False,
                skip_checking=False,
            )
            print(f"✓ Added {r['torfile'].name}")


if __name__ == "__main__":
    main()
