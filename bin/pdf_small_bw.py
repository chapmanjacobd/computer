#!/usr/bin/python3
import argparse
import os
import tempfile
from pathlib import Path

from xklb.utils import processes


def convert_images_to_pdf(directory, resize=1000):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        output_pdfs = []
        for filepath in Path(directory).iterdir():
            temp_pbm = temp_dir_path / 'temp.pbm'
            output_pdf = temp_dir_path / filepath.with_suffix('.pdf').name

            processes.cmd('convert', str(filepath), '-resize', f'{resize}>', str(temp_pbm))
            processes.cmd('convert', str(temp_pbm), '-alpha', 'off', '-monochrome', '-compress', 'fax', str(output_pdf))

            output_pdfs.append(output_pdf)

        pdf_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.lower().endswith('.pdf')]
        pdf_files.sort()
        processes.cmd('mutool', 'merge', '-o', 'out.pdf', *pdf_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert images in a directory to a combined PDF')
    parser.add_argument('directory', help='Path to the directory containing images')
    parser.add_argument(
        '-r', '--resize', type=int, default=1000, help='Resize images to the specified width (default: 1000)'
    )
    args = parser.parse_args()

    convert_images_to_pdf(args.directory, args.resize)
