#!/usr/bin/python3
import argparse
import os
import shutil
import subprocess
import tempfile

import tenacity


def curl(curl_cmd):
    cwd = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)

    subprocess.run(curl_cmd, shell=True)

    files = os.listdir(temp_dir)
    if len(files) != 1:
        raise Exception(f"Expected 1 file in temp directory {temp_dir}, found {str(len(files))}")
    downloaded_file = files[0]
    downloaded_file = shutil.move(downloaded_file, cwd)

    shutil.rmtree(temp_dir)
    os.chdir(cwd)

    return downloaded_file


@tenacity.retry(wait=tenacity.wait_exponential(multiplier=3, min=30, max=900))
def curl_with_filetype(curl_cmd, expected_type):
    downloaded_file = curl(' '.join(curl_cmd))

    output = subprocess.check_output(['file', '-bi', downloaded_file])
    if expected_type not in output.decode('utf-8'):
        raise Exception("File type does not match")

    return downloaded_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-type","--filetype", help="Expected file type")
    parser.add_argument("--move", help="Path to move file to on success")

    parser.add_argument("curl_cmd", nargs='+', help="Curl command to run")
    args = parser.parse_args()

    try:
        successful_download = curl_with_filetype(args.curl_cmd, args.file_type)
    except Exception as e:
        print(args.curl_cmd)
        print(e)
        raise SystemExit(1)
    else:
        if args.move:
            shutil.move(successful_download, args.move)
