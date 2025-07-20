#!/usr/bin/python3
import os
import shutil
from collections import defaultdict
from pathlib import Path

from library.utils import arggroups, argparse_utils, consts
from torrentool.api import Torrent


def get_file_extension(filepath):
    return os.path.splitext(filepath)[1].lstrip('.').lower()


def categorize_file(filename):
    ext = get_file_extension(filename)

    if ext in consts.PLAIN_EXTENSIONS | consts.CALIBRE_EXTENSIONS:
        return 'books'
    elif ext in consts.AUDIO_ONLY_EXTENSIONS:
        return 'audio'
    elif ext in consts.VIDEO_EXTENSIONS | consts.IMAGE_ANIMATION_EXTENSIONS:
        return 'video'
    elif ext in consts.IMAGE_EXTENSIONS:
        return 'images'
    elif ext in consts.ARCHIVE_EXTENSIONS:
        return 'archives'
    elif ext in consts.HTML_SIDECAR_EXTENSIONS | consts.OCRMYPDF_EXTENSIONS | consts.OCR_EXTENSIONS:
        return 'documents'
    else:
        return 'other'


def analyze_torrent_content(files):
    if not files:
        return 'empty'

    category_counts = defaultdict(int)
    category_sizes = defaultdict(int)

    for file_info in files:
        file_path, file_size = file_info

        category = categorize_file(file_path)
        category_counts[category] += 1
        category_sizes[category] += file_size

    total_files = sum(category_counts.values())
    total_size = sum(category_sizes.values())

    if total_files == 0:
        return 'empty'

    # Score = (count / total_files) * (size / total_size)
    # This gives more weight to categories with many large files
    category_scores = {}
    for category in category_counts:
        count_weight = category_counts[category] / total_files
        size_weight = category_sizes[category] / total_size if total_size > 0 else 0
        category_scores[category] = count_weight * size_weight

    sorted_categories = sorted(category_scores.items(), key=lambda item: item[1], reverse=True)
    if not sorted_categories:
        return 'unknown'

    main_category, main_score = sorted_categories[0]
    if len(sorted_categories) > 1 and main_score < 0.5:
        return 'mixed'

    return main_category


if __name__ == '__main__':
    parser = argparse_utils.ArgumentParser()
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser)
    args = parser.parse_args()

    paths: list[Path] = []
    for p in args.paths:
        p = Path(p)
        if p.is_dir():
            paths.extend(p.glob("*.torrent"))
        else:
            paths.append(p)

    for torrent_file in paths:
        torrent = Torrent.from_file(torrent_file)

        primary_category = analyze_torrent_content(torrent.files)
        target_directory = os.path.join(os.path.dirname(torrent_file), primary_category)

        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        target_file = os.path.join(target_directory, os.path.basename(torrent_file))
        shutil.move(torrent_file, target_file)
