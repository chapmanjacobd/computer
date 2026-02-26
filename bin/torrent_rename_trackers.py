#!/usr/bin/python3
from concurrent.futures import ThreadPoolExecutor
import libtorrent as lt

from library.mediafiles.torrents_dump import gen_torrents
from library.utils import arggroups, argparse_utils

parser = argparse_utils.ArgumentParser()

parser.add_argument(
    "--replace",
    "--rename",
    default=[],
    action=argparse_utils.ArgparseList,
    help="Substring replacements in the form OLD=NEW",
)

arggroups.debug(parser)
parser.add_argument("paths", nargs="+", help="Path(s) to torrent files")
args = parser.parse_args()

# Parse replacements into byte pairs
replacements = []
for item in args.replace:
    if "=" not in item:
        raise ValueError(f"Invalid --replace value: {item} (expected OLD=NEW)")
    old, new = item.split("=", 1)
    replacements.append((old.encode("utf-8"), new.encode("utf-8")))


def rewrite_url(url: bytes):
    original = url
    for old, new in replacements:
        if old in url:
            url = url.replace(old, new)
    return original, url


def rewrite_trackers(path):
    with open(path, "rb") as f:
        torrent_data = lt.bdecode(f.read())  # type: ignore

    changes = []

    # Rewrite announce-list
    if b"announce-list" in torrent_data:
        new_announce_list = []
        for tier in torrent_data[b"announce-list"]:
            new_tier = []
            for tracker_url in tier:
                old_url, new_url = rewrite_url(tracker_url)
                if old_url != new_url:
                    changes.append(
                        (old_url.decode("utf-8", "replace"),
                         new_url.decode("utf-8", "replace"))
                    )
                new_tier.append(new_url)
            new_announce_list.append(new_tier)
        torrent_data[b"announce-list"] = new_announce_list

    # Rewrite single announce
    if b"announce" in torrent_data:
        old_url, new_url = rewrite_url(torrent_data[b"announce"])
        if old_url != new_url:
            changes.append(
                (old_url.decode("utf-8", "replace"),
                 new_url.decode("utf-8", "replace"))
            )
        torrent_data[b"announce"] = new_url

    # Only print if changes occurred
    if changes:
        print(f"\n{path}")
        for old, new in changes:
            print(f"  {old}")
            print(f"    -> {new}")

        if not args.simulate:
            with open(path, "wb") as f:
                f.write(lt.bencode(torrent_data))  # type: ignore


torrent_files = list(gen_torrents(args.paths))

with ThreadPoolExecutor(max_workers=1) as executor:
    futures = [executor.submit(rewrite_trackers, f) for f in torrent_files]
    for future in futures:
        future.result()
