#!/usr/bin/python3
import os

from library.utils import shell_utils, arggroups, argparse_utils


def read_in_chunks(file_object, chunk_size=1024 * 1024 * 256):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def check_file(args, path):
    try:
        with open(path, 'rb') as f:
            for _ in read_in_chunks(f):
                pass  # do nothing
    except OSError as e:
        if e.errno == 5:  # Input/output error
            print(path)
            if args.remove:
                try:
                    os.unlink(path)
                except OSError as unlink_e:
                    print(f"Failed to remove {path}: {unlink_e}")
        else:
            print(f"{path}: {e}")


def rm_corrupt():
    parser = argparse_utils.ArgumentParser()
    parser.add_argument('--remove', '-r', action='store_true', help='Actually remove files')
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser)
    args = parser.parse_args()
    arggroups.args_post(args, parser)

    for path in shell_utils.gen_paths(args):
        check_file(args, path)


if __name__ == "__main__":
    rm_corrupt()
