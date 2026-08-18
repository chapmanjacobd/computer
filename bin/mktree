#!/usr/bin/python3
import os
from pathlib import Path

from library.utils import argparse_utils

tasks = ['dump', 'check', 'library', 'archive']
categories = {
    'self': ['metadata', 'home', 'finances', 'secure', 'private', 'credentials', 'portraits', 'other'],
    'world': ['consulting', 'downloads', 'seeding', 'other'],
    'datasets': ['raster', 'vector', 'links', 'file-lists', 'social', 'other'],
    'programs': ['linux', 'windows', 'repos', 'other'],
    'games': ['8bit', 'gamecube', 'wii', 'switch', 'vr', 'linux', 'other'],
    'text': ['ebooks', 'manga', 'receipts', 'web', 'recipes', 'theory', 'other'],
    'porn': ['video', 'vr', 'audio', 'image', 'other'],
    'video': ['other'],
    'audio': ['music', 'audiobooks', 'midi', 'patterns', 'recordings', 'other'],
    'image': ['art', 'memes', 'patterns', 'other'],
    'internals': ['text', 'video', 'audio', 'image', 'other'],
    'projects': ['art', 'cinematograph', 'music', 'other'],
}


def create_directory_structure(base_dir):
    structure = set()
    for task in tasks:
        structure.add(str(Path(base_dir, task)))

        for category, subcategories in categories.items():
            path = str(Path(base_dir, task, category))
            os.makedirs(path, exist_ok=True)
            structure.add(path)

            for subcategory in subcategories:
                path = str(Path(base_dir, task, category, subcategory))
                os.makedirs(path, exist_ok=True)
                structure.add(path)

    return structure

def check_directory_structure(base_path, expected_structure):
    def check_path(dir):
        for p in dir.glob("*"):
            if str(p).count(os.sep) > str(base_path).count(os.sep) + 3:
                continue

            if not p.is_dir():
                print(p)
            else:
                if str(p) not in expected_structure:
                    print(p)
                else:
                    check_path(p)
    check_path(base_path)

if __name__ == "__main__":
    parser = argparse_utils.ArgumentParser(description='Create directory hierarchy.')
    parser.add_argument('base_dir', nargs='?', default=os.getcwd())
    args = parser.parse_args()

    args.base_dir = Path(args.base_dir).absolute()

    structure = create_directory_structure(args.base_dir)
    check_directory_structure(args.base_dir, structure)
