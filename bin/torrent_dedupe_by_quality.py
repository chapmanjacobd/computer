#!/usr/bin/python3
import re
import sqlite3
from collections import defaultdict

from library.utils import arggroups, argparse_utils, consts, devices, strings
from library.utils.log_utils import log

QUALITIES = [
    "576p",
    "540p",
    "720p",
    "480p",
    "hdtv",
    "1080p",
    "1080",
    "x265",
    "x264",
    "h264",
    "web-dl",
    "web.dl",
    "web",
    "webrip",
    "bdrip",
    "brrip",
    "dvd",
    "dvdrip",
    "hdrip",
    "hd",
    "720i",
    "540i",
    "480i",
    "1080i",
    "xvid",
    "divx6",
    "divx521",
    "divx511",
    "divx5",
    "divx",
    "2160p",
    "uhdtv",
    "4k",
    "dvb",
    "pdtv",
    "tvcap",
    "vhsrip",
    "ac3",
    "aac",
    "mp3",
    "mg2",
]

REGEX_QUALITY = re.compile(r"\.(" + "|".join(map(re.escape, QUALITIES)) + r").*\.torrent$", re.I)
REGEX_VIDEO_EXT = re.compile(r'\.(' + '|'.join(consts.VIDEO_EXTENSIONS | consts.AUDIO_ONLY_EXTENSIONS) + r')\.', re.I)

QUALITY_MAP = {q: i for i, q in enumerate(QUALITIES)}


def prioritize_resolution(path):
    for s in path.lower().split("."):
        for quality, i in QUALITY_MAP.items():
            if quality in s:
                return i

    log.info("resolution not found %s", path)
    return len(QUALITIES)


def extract_base_name(path):
    base_name = REGEX_QUALITY.sub('', path.rsplit("/")[-1])
    base_name = REGEX_VIDEO_EXT.sub('.', base_name)
    return strings.path_to_sentence(base_name)


def seep(filename):
    patterns = {
        'xofy': r'(\d+)\s?of\s?(\d+)',  # 04of26 -> (4, 26)
        'part': r'Part\s?(\d+)',  # Part1 -> 1
        'episode': r'[Ee]pisode\s?(\d+)',
        'season_ep': r'[Ss]\s?(\d+)[Ee]\s?(\d+)',
    }

    for pattern_type, pattern in patterns.items():
        match = re.search(pattern, filename)
        if match:
            if pattern_type == 'xofy':
                return f"{match.group(1).lstrip('0')}of{match.group(2).lstrip('0')}"  # Normalize: 04of26 -> 4of26
            elif pattern_type == 'part':
                return f"Part{match.group(1).lstrip('0')}"  # Normalize: Part04 -> Part4
            elif pattern_type == 'season_ep':
                return f"S{match.group(1).lstrip('0')}E{match.group(2).lstrip('0')}"
            else:
                return match.group(1)

    return None


def group_episodes(bases):
    groups = {}

    for base in bases:
        key = seep(base)  # can be None :-)
        if key not in groups:
            groups[key] = []
        groups[key].append(base)

    return list(groups.values())


def cluster_paths(args, all_paths):
    clusters = []
    processed = set()

    base_names = {path: extract_base_name(path) for path in all_paths}
    unique_bases = list(set(base_names.values()))

    if args.similar is not None:
        from rapidfuzz import fuzz, process

        threshold = args.similar * 100 if (0 <= args.similar <= 1) else args.similar

        for base in unique_bases:
            if base in processed:
                continue

            matches = process.extract(base, unique_bases, scorer=fuzz.ratio, score_cutoff=threshold)

            similar_bases = {match[0] for match in matches}
            similar_episodes = group_episodes(similar_bases)
            for similar_bases in similar_episodes:
                cluster_paths = [path for path, base_name in base_names.items() if base_name in similar_bases]

                if len(cluster_paths) > 1:
                    clusters.append(cluster_paths)
                    processed.update(similar_bases)
                else:
                    log.debug("Could not find enough matches %s", base)

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
        if len(similar_paths) == 1:
            print('MATCHING:', similar_paths[0])
        else:
            print('MATCHES:')
            for s in similar_paths:
                print("\t", s)

        duplicates.update(similar_paths)
        print()

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
        "--similar", nargs="?", type=float, const=100, help="Similarity ratio for comparing filenames (0.0-1.0)"
    )
    arggroups.debug(parser)

    parser.add_argument("database", help="Path to the SQLite database.")
    args = parser.parse_args()
    arggroups.args_post(args, parser)

    dedupe_database(args)
