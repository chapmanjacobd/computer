#!/usr/bin/env python3

import argparse
from pathlib import Path
import random

PLAIN_EXTENSIONS = {'txt', 'pdf', 'epub', 'mobi'}
CALIBRE_EXTENSIONS = {'azw', 'azw3'}
AUDIO_ONLY_EXTENSIONS = {'mp3', 'flac', 'wav'}
VIDEO_EXTENSIONS = {'mp4', 'mkv', 'avi'}
IMAGE_ANIMATION_EXTENSIONS = {'gif'}
IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ARCHIVE_EXTENSIONS = {'zip', 'rar', '7z'}
HTML_SIDECAR_EXTENSIONS = {'html'}
OCR_EXTENSIONS = {'hocr'}
ALL_EXTENSIONS = (
    PLAIN_EXTENSIONS
    | CALIBRE_EXTENSIONS
    | AUDIO_ONLY_EXTENSIONS
    | VIDEO_EXTENSIONS
    | IMAGE_ANIMATION_EXTENSIONS
    | IMAGE_EXTENSIONS
    | ARCHIVE_EXTENSIONS
    | HTML_SIDECAR_EXTENSIONS
    | OCR_EXTENSIONS
)


def create_empty_file(filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.touch()


def create_test_folder_structure(args):
    test_root = Path(args.path)

    print(f"Creating test directory at '{test_root}'...")

    # Scenario 1: A simple folder with a clear primary category
    books_dir = test_root / "test_books_folder"
    books_dir.mkdir(parents=True, exist_ok=True)
    create_empty_file(books_dir / "book1.epub")
    create_empty_file(books_dir / "book2.pdf")
    create_empty_file(books_dir / "document.txt")  # A text file should also be categorized as 'books'

    # Scenario 2: A folder with a 'mixed' category, no clear winner
    mixed_dir = test_root / "mixed_media_folder"
    mixed_dir.mkdir(parents=True, exist_ok=True)
    create_empty_file(mixed_dir / "vacation_video.mp4")
    create_empty_file(mixed_dir / "selfie.jpg")
    create_empty_file(mixed_dir / "podcast_ep1.mp3")
    create_empty_file(mixed_dir / "resume.pdf")

    # Scenario 3: A folder with an "other" file type
    other_dir = test_root / "other_files"
    other_dir.mkdir(parents=True, exist_ok=True)
    create_empty_file(other_dir / "program_source.py")
    create_empty_file(other_dir / "configuration.cfg")
    create_empty_file(other_dir / "readme.md")

    # Scenario 4: A folder that is empty, to test the 'empty' category
    empty_dir = test_root / "empty_folder"
    empty_dir.mkdir(parents=True, exist_ok=True)

    # Scenario 5: Interesting depth testing scenarios
    # A single deep path with different content at each level
    current_path = test_root / "deep_path"
    for i in range(args.depth):
        current_path = current_path / f"level_{i+1}"
        current_path.mkdir(parents=True, exist_ok=True)
        # Add a random file at each depth to make it interesting
        all_exts = list(ALL_EXTENSIONS)
        random_ext = random.choice(all_exts)
        create_empty_file(current_path / f"file_{i}.{random_ext}")

    # Scenario 6: A wide but shallow structure to test depth=1
    wide_dir = test_root / "wide_test"
    wide_dir.mkdir(parents=True, exist_ok=True)
    for i in range(5):
        sub_dir = wide_dir / f"sub_dir_{i}"
        sub_dir.mkdir(parents=True, exist_ok=True)
        # Create a specific category folder inside
        if i == 0:  # books
            create_empty_file(sub_dir / "books.epub")
        elif i == 1:  # video
            create_empty_file(sub_dir / "video.mp4")
        elif i == 2:  # images
            create_empty_file(sub_dir / "images.jpg")
        elif i == 3:  # archives
            create_empty_file(sub_dir / "archives.zip")
        else:  # other
            create_empty_file(sub_dir / "other.exe")


def main():
    parser = argparse.ArgumentParser(description="Generate a test folder structure for a file sorting program.")
    parser.add_argument(
        "--path",
        "-p",
        type=str,
        default="test_data",
        help="The root directory for the test data. Will be created if it doesn't exist. "
        "Existing data will be removed. (default: 'test_data')",
    )
    parser.add_argument(
        "--depth", "-D", type=int, default=3, help="The maximum depth of nested directories for testing. (default: 3)"
    )

    args = parser.parse_args()
    create_test_folder_structure(args)


if __name__ == '__main__':
    main()
