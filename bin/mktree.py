#!/usr/bin/python3
import argparse
import os

tasks = ['sync', 'dump', 'check', 'library', 'archive']
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
    for task in tasks:
        for category, subcategories in categories.items():
            path = os.path.join(base_dir, task, category)
            os.makedirs(path, exist_ok=True)

            for subcategory in subcategories:
                path = os.path.join(base_dir, task, category, subcategory)
                os.makedirs(path, exist_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create directory hierarchy.')
    parser.add_argument('base_dir', nargs='?', default=os.getcwd())
    args = parser.parse_args()

    create_directory_structure(args.base_dir)
