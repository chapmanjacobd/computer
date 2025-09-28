#!/usr/bin/python3
import re
import sqlite3
from collections import defaultdict
from difflib import SequenceMatcher

from library.utils import arggroups, argparse_utils, consts, devices, strings
from library.utils.log_utils import log

QUALITIES = [
    "720p",
    "HDTV",
    "1080p",
    "x265",
    "x264",
    "720i",
    "1080i",
    "BRrip",
    "DVD",
    "DVDRip",
    "XviD",
    "4K",
    "PDTV",
]

REGEX_QUALITY = re.compile(r"\.(" + "|".join(map(re.escape, QUALITIES)) + r").*\.torrent$", re.I)
REGEX_VIDEO_EXT = re.compile(r'\.(' + '|'.join(consts.VIDEO_EXTENSIONS | consts.AUDIO_ONLY_EXTENSIONS) + r')\.', re.I)


def prioritize_resolution(path):
    for i, quality in enumerate(QUALITIES):
        if quality.lower() in path.lower():
            return i
    log.info("resolution not found %s", path)
    return len(QUALITIES)


def extract_base_name(path):
    base_name = REGEX_QUALITY.sub('', path)
    base_name = REGEX_VIDEO_EXT.sub('.', base_name)
    return strings.path_to_sentence(base_name)


def cluster_paths(args, all_paths):
    clusters = []
    processed = set()

    base_names = {path: extract_base_name(path) for path in all_paths}

    if args.similar is not None:
        threshold = args.similar if (0 <= args.similar <= 1) else args.similar / 100

        # Group by similarity
        paths_list = list(base_names.items())
        n = len(paths_list)

        for i in range(n):
            path_i, base_i = paths_list[i]
            if base_i in processed:
                continue
            cluster = [path_i]
            for j in range(i + 1, n):
                path_j, base_j = paths_list[j]
                if base_j in processed:
                    continue
                if SequenceMatcher(None, base_i, base_j).ratio() >= threshold:
                    cluster.append(path_j)
                    processed.add(base_j)
            if len(cluster) > 1:
                clusters.append(cluster)
            processed.add(base_i)

    else:
        # Group by exact base name
        groups = defaultdict(list)
        for path, base in base_names.items():
            groups[base].append(path)
        clusters = [grp for grp in groups.values() if len(grp) > 1]

    return clusters


def dedupe_database(args):
    conn = sqlite3.connect(args.database)
    cursor = conn.cursor()

    cursor.execute("SELECT path FROM media WHERE time_deleted=0")
    all_paths = [row[0] for row in cursor.fetchall()]

    clusters = cluster_paths(args, all_paths)
    duplicates = set()

    for similar_paths in clusters:
        best_path = min(similar_paths, key=prioritize_resolution)
        print('ORIGINAL:', best_path)
        similar_paths.remove(best_path)
        print('DUPLICATES:', similar_paths)
        duplicates.update(similar_paths)

    if len(duplicates) == 0:
        print('No duplicates found')
    else:
        if devices.confirm(f'Mark {len(duplicates)} as deleted?'):
            for path in duplicates:
                cursor.execute("UPDATE media SET time_deleted = unixepoch('now') WHERE path = ?", [path])
            conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse_utils.argparse.ArgumentParser(description="Deduplicate media files in a database.")
    parser.add_argument(
        "--similar", nargs="?", type=float, const=0.8, help="Similarity ratio for comparing filenames (0.0-1.0)"
    )
    arggroups.debug(parser)

    parser.add_argument("database", help="Path to the SQLite database.")
    args = parser.parse_args()
    arggroups.args_post(args, parser)

    dedupe_database(args)
