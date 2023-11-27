#!/usr/bin/python3
import os
from collections import defaultdict
from pathlib import Path

import rarfile

cwd = Path().cwd()

destination_base = Path('..', os.path.basename(cwd) + '_out')
destination_base.mkdir(exist_ok=True)  # TODO: remove


def check_archive(input_path: Path):
    files = defaultdict(list)
    with rarfile.RarFile(input_path, errors='strict') as rf:
        rf.setpassword('heshui')

        for f in rf.infolist():
            if f.file_size == 0:
                if not f.filename.endswith(os.sep):
                    print(f.filename)
                continue
            elif f.filename.endswith('.jpg'):
                continue

            files[os.path.splitext(f.filename)[1]].append((f.filename, f.mtime))

        if len(files.keys()) == 0:
            print('No files:', input_path)
        elif len(files.keys()) == 1:
            for _, files_arr in files.items():
                for member, mtime in files_arr:
                    print(member, mtime)
                    # rf.extract(member, destination_base)
        else:
            print(files)


for input_path in cwd.rglob('*'):
    if input_path.is_file():
        try:
            check_archive(input_path)
        except (rarfile.BadRarFile, rarfile.NotRarFile):
            print('Corrupt file:', input_path)
        except rarfile.NeedFirstVolume:
            print('NeedFirstVolume', input_path)
        except Exception as e:
            print(input_path)
            raise
