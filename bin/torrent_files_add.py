#!/usr/bin/env python3

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import libtorrent as lt
from library.mediafiles import torrents_start
from library.utils import arggroups, devices, strings


def compute_save_path(local_path: Path, torrent_rel_path: str) -> Path:
    """Compute the save path by walking up from the local file."""
    depth = len(Path(torrent_rel_path).parts)
    save_path = local_path
    for _ in range(depth):
        save_path = save_path.parent
    return save_path


def main():
    parser = argparse.ArgumentParser(description="Add torrents if files with matching names/sizes exist locally")
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    parser.add_argument("--threshold", type=float, default=95.0, help="Percentage of torrent size that must match")
    parser.add_argument("torrent_dir", type=Path)
    parser.add_argument("search_dirs", nargs="+", type=Path)

    args = parser.parse_args()

    limits = {
        "max_buffer_size": 55_000_000,
        "max_pieces": 2_000_000,
        "max_decode_tokens": 5_000_000,
    }

    # Load all torrents
    torrents = []
    for torrent_file in args.torrent_dir.glob("*.torrent"):
        try:
            ti = lt.torrent_info(str(torrent_file), limits)
            torrents.append(
                {
                    "ti": ti,
                    "torrent_file": torrent_file,
                    "fs": ti.files(),
                }
            )
        except Exception as e:
            print(f"[ERROR] {torrent_file}: {e}")

    print(f"Loaded {len(torrents)} torrents")

    size_index = {}
    for t in torrents:
        ti = t["ti"]
        fs = t["fs"]

        for i in range(ti.num_files()):
            size = fs.file_size(i)
            path = fs.file_path(i)
            size_index.setdefault(size, []).append(
                {
                    "file_index": i,
                    "ti": ti,
                    "fs": fs,
                    "torrent_file": t["torrent_file"],
                    "torrent_rel_path": path,
                }
            )

    # Initialize progress tracking for each torrent
    progress = {}
    for t in torrents:
        ti = t["ti"]
        infohash = ti.info_hash().to_string()

        progress[infohash] = {
            "total_size": ti.total_size(),
            "ti": ti,
            "torrent_file": t["torrent_file"],
            "save_path_hits": {},  # Path -> matched_size
        }

    # Collect all local files
    candidates = []
    for d in args.search_dirs:
        if not d.exists():
            print(f"[WARNING] Missing directory: {d}")
            continue
        candidates.extend(f for f in d.rglob("*") if f.is_file())

    print(f"Scanning {len(candidates)} files")

    # Match local files to torrent files
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(lambda f: (f, f.stat().st_size), f) for f in candidates}

        for future in as_completed(futures):
            local_file, size = future.result()

            for entry in size_index.get(size, []):
                ti = entry["ti"]
                fs = entry["fs"]
                torrent_rel_path = entry["torrent_rel_path"]
                if not str(local_file).endswith(torrent_rel_path):
                    continue

                infohash = ti.info_hash().to_string()
                prog = progress[infohash]

                candidate_save_path = compute_save_path(local_file, torrent_rel_path)

                # Credit size to this specific save_path hypothesis
                prog["save_path_hits"].setdefault(candidate_save_path, 0)
                prog["save_path_hits"][candidate_save_path] += size

    results = []
    for p in progress.values():
        if not p["total_size"]:
            continue

        save_path_hits = p["save_path_hits"]
        if not save_path_hits:
            continue

        if len(save_path_hits) > 1:
            # Choose save_path with maximum matched bytes
            save_path_hits = sorted(save_path_hits.items(), key=lambda kv: (kv[1], -len(kv[0].parts)))

            print("  competing save paths:")
            for sp, sz in save_path_hits:
                print(f"    {sp} -> {strings.file_size(sz)}")
        best_save_path, best_matched = save_path_hits[0]

        pct = (best_matched / p["total_size"]) * 100
        if pct < args.threshold:
            continue

        results.append(
            {
                "ti": p["ti"],
                "torrent_file": p["torrent_file"],
                "save_path": best_save_path,
                "matched_size": best_matched,
                "total_size": p["total_size"],
                "pct": pct,
            }
        )

    results.sort(key=lambda r: (-r["pct"], r["total_size"]))
    print(f"\nFound {len(results)} torrents ≥ {args.threshold}%")

    for r in results:
        print(
            f"\n{r['torrent_file'].name} ({r['save_path']} {r['ti'].name()}): "
            f"{r['pct']:.1f}% "
            f"({strings.file_size(r['matched_size'])}/"
            f"{strings.file_size(r['total_size'])})"
        )

    if devices.confirm("Add to qBittorrent?"):
        qbt_client = torrents_start.start_qBittorrent(args)

        for r in results:
            if r["save_path"] is None:
                print("  [WARNING] No save path determined!, skipping", r["torrent_file"])
                continue

            qbt_client.torrents_add(
                torrent_files=open(r["torrent_file"], "rb"),
                download_path=str(r["save_path"]),
                save_path=str(r["save_path"]),
                use_auto_torrent_management=False,
                is_paused=False,
                skip_checking=False,
                add_to_top_of_queue=False,
            )
            print(f"✓ Added {r['torrent_file'].name}")


if __name__ == "__main__":
    main()
