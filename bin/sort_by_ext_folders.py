#!/usr/bin/python3
import os
import shutil
from collections import defaultdict
from pathlib import Path

from library.utils import arggroups, argparse_utils, consts


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


def analyze_folder(files):
    if not files:
        return 'empty'

    category_counts = defaultdict(int)
    category_sizes = defaultdict(int)

    for file_path in files:
        category = categorize_file(file_path)
        category_counts[category] += 1
        category_sizes[category] += os.stat(file_path).st_size

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
        category_scores[category] = count_weight * (size_weight * 4)

    sorted_categories = sorted(category_scores.items(), key=lambda item: item[1], reverse=True)
    if not sorted_categories:
        return 'unknown'

    main_category, main_score = sorted_categories[0]
    if len(sorted_categories) > 1 and main_score < 0.5:
        return 'mixed'

    return main_category


def sort_by_ext(args):
    paths: list[Path] = []
    for p in args.paths:
        p = Path(p)
        if p.is_dir():
            if args.depth > 0:
                start_depth = len(p.parts)
                paths.extend([sp for sp in p.rglob("*") if args.depth == (len(sp.parts) - start_depth) and sp.is_dir()])
            else:
                paths.append(p)

    for folder in paths:
        files = [sp for sp in folder.rglob("*") if not sp.is_dir()]
        primary_category = analyze_folder(files)

        if args.destination:
            parent = args.destination
        else:
            parent = os.path.dirname(folder)
            for _ in range(args.depth):
                parent = os.path.dirname(parent)

        target_directory = os.path.join(parent, primary_category)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        target_path = os.path.join(target_directory, os.path.basename(folder))
        shutil.move(folder, target_path)


if __name__ == '__main__':
    parser = argparse_utils.ArgumentParser()
    parser.add_argument("--destination", "--dest")
    parser.add_argument("--depth", "-D", type=int, default=0)
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser)
    args = parser.parse_args()

    sort_by_ext(args)
