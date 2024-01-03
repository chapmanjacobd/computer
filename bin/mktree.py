#!/usr/bin/python3
import argparse
import os

tasks = ['sync', 'dump', 'check', 'library', 'archive']
categories = {
    'self': [],
    'world': [],
    'datasets': [],
    'programs': [],
    'games': ['VR'],
    'text': [],
    'porn': ['video', 'VR', 'audio', 'image'],
    'video': [],
    'audio': [],
    'image': [],
}


def create_directory_structure(base_dir):
    for task in tasks:
        for category, subcategories in categories.items():
            path = os.path.join(base_dir,task, category)
            os.makedirs(path, exist_ok=True)

            for subcategory in subcategories:
                path = os.path.join(base_dir, task, category, subcategory)
                os.makedirs(path, exist_ok=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create directory hierarchy.')
    parser.add_argument('base_dir', nargs='?', default=os.getcwd(), help='Base directory path (default: current working directory)')
    args = parser.parse_args()

    create_directory_structure(args.base_dir)
