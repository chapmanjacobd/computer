#!/usr/bin/python3
from pathlib import Path

from library.utils import arg_utils, arggroups, argparse_utils, shell_utils


def cp_tree():
    parser = argparse_utils.ArgumentParser(description='Copy filenames and directorynames recursively')
    parser.add_argument('--files-only', '-tf', action='store_true', help='Copy files only')
    parser.add_argument('--folders-only', '-td', action='store_true', help='Copy folders only')

    parser.add_argument('--folder-prefix', default='', help='Prefix for new folder names')
    parser.add_argument('--file-prefix', default='', help='Prefix for new file names')

    parser.add_argument('--folder-suffix', default='', help='Suffix for new folder names')
    parser.add_argument('--file-suffix', default='', help='Suffix for new file names')
    parser.add_argument('--file-ext', default='', help='Ext for new file names')
    arggroups.debug(parser)

    parser.add_argument('source', help='Source directory')
    parser.add_argument('destination', help='Destination directory')
    args = parser.parse_args()
    arggroups.args_post(args, parser)

    source_folder, source_glob = arg_utils.split_folder_glob(args.source)
    source_folder = source_folder.resolve()

    if source_glob != '*' and args.ext:
        raise NotImplementedError

    if source_glob != '*':
        found = source_folder.rglob(source_glob)
        folders = set(p for p in found if p.is_dir())
        files = set(p for p in found if not p.is_dir())
    else:
        files, _, folders = shell_utils.rglob(str(source_folder), args.ext or None)

    dst = Path(args.destination).resolve()

    if not args.files_only:
        for folder in folders:
            p = Path(folder).relative_to(source_folder)
            p = dst / p.parent / (args.folder_prefix + p.name + args.folder_suffix)
            if not p.exists():
                if args.simulate:
                    print('mkdir', p)
                else:
                    p.mkdir(parents=True, exist_ok=True)

    if not args.folders_only:
        for file in files:
            p = Path(file).relative_to(source_folder)
            p = dst / p.parent / (args.file_prefix + p.stem + args.file_suffix + p.suffix + args.file_ext)
            if not p.exists():
                if args.simulate:
                    print('touch', p)
                else:
                    p.touch(exist_ok=True)


if __name__ == "__main__":
    cp_tree()
