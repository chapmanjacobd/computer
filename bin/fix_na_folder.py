#!/usr/bin/python3
import argparse
import os
import shutil

from library.utils import arggroups, consts, objects, processes
from library.utils.log_utils import log

media_extensions = tuple("." + ext for ext in consts.VIDEO_EXTENSIONS | consts.AUDIO_ONLY_EXTENSIONS)


def move_na_files(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        if "na" in dirs:
            relative_path = os.path.relpath(root, input_dir)

            na_dir = os.path.join(root, "na")
            for filename in os.listdir(na_dir):
                if not filename[:5].lower().endswith(media_extensions):
                    continue

                filepath = os.path.join(na_dir, filename)
                if os.path.isfile(filepath):
                    probe = processes.FFProbe(filepath)
                    artist = objects.traverse_obj(probe.audio_streams, [0, "tags", "artist"])

                    if artist:
                        artist_dir = os.path.join(output_dir, relative_path, str(artist))
                        os.makedirs(artist_dir, exist_ok=True)
                        destination_path = os.path.join(artist_dir, filename)

                        if os.path.exists(destination_path):
                            log.warning(f"Skipping file %s already exists in %s", filename, artist_dir)
                        else:
                            shutil.move(filepath, destination_path)

                    else:
                        artist_dir = os.path.join(output_dir, relative_path, 'no_artist')
                        os.makedirs(artist_dir, exist_ok=True)
                        destination_path = os.path.join(artist_dir, filename)

                        if os.path.exists(destination_path):
                            log.warning(f"Skipping file %s already exists in %s", filename, artist_dir)
                        else:
                            shutil.move(filepath, destination_path)


def main():
    parser = argparse.ArgumentParser(description="Move files from 'na' folders to artist-named folders.")
    arggroups.debug(parser)

    parser.add_argument("input_dir", help="The root directory to search for 'na' folders.")
    parser.add_argument("output_dir", help="The directory to move files to.")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    move_na_files(input_dir, output_dir)


if __name__ == "__main__":
    main()
