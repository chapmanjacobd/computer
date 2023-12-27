#!/usr/bin/python3
import argparse
import tempfile
from pathlib import Path
from natsort import natsorted
from xklb.utils import processes


def convert_images_to_pdf(directory, resize):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        output_pdfs = []
        for filepath in natsorted(Path(directory).iterdir()):
            temp_pbm = temp_dir_path / 'temp.pbm'
            output_pdf = temp_dir_path / filepath.with_suffix('.pdf').name

            processes.cmd('convert', str(filepath), '-resize', f'{resize}>', str(temp_pbm))
            processes.cmd('convert', str(temp_pbm), '-alpha', 'off', '-monochrome', '-compress', 'fax', str(output_pdf))
            output_pdfs.append(output_pdf)

        processes.cmd('mutool', 'merge', '-o', 'out.pdf', *output_pdfs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert images in a directory to a combined PDF')
    parser.add_argument('directory', help='Path to the directory containing images')
    parser.add_argument(
        '-r', '--resize', type=int, default=1000, help='Resize images to the specified width (default: 1000)'
    )
    args = parser.parse_args()

    convert_images_to_pdf(args.directory, args.resize)
