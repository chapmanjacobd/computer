#!/usr/bin/python3
import argparse
import os
from collections import defaultdict
from pathlib import Path
from xklb.utils import objects
from xklb.utils.log_utils import log
import rarfile

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", "-v", action="count", default=0)

    parser.add_argument("source_path", type=Path, default=Path.cwd())
    args = parser.parse_intermixed_args()

    log.info(objects.dict_filter_bool(args.__dict__))
    return args


def check_archive(args, input_path: Path, output_prefix: Path):
    files = defaultdict(list)
    with rarfile.RarFile(input_path, errors='strict') as rf:
        rf.setpassword('heshui')

        for f in rf.infolist():
            if f.file_size == 0:
                if not f.filename.endswith(os.sep):
                    log.warning('Ignoring non-directory zero size file:', f.filename)
                continue
            elif f.filename.endswith(('.txt', '.jpg')):
                continue

            files[os.path.splitext(f.filename)[1]].append((f.filename, f.mtime))

        if len(files.keys()) == 0:
            log.error('No files found in:', input_path)
        elif len(files.keys()) == 1:
            for ext, files_arr in files.items():
                for member, mtime in files_arr:
                    log.debug('One type of extension (%s): %s', ext, member)
                    if not args.dry_run:
                        rf.extract(member, output_prefix)
        else:
            log.debug('Directory structure not recognized: %s', files)



if __name__ == "__main__":
    args = parse_args()

    src = args.source_path
    output_prefix = src.parent / (src.parent.name + '_out')
    output_prefix.mkdir(exist_ok=args.dry_run)

    for input_path in src.rglob('*'):
        if input_path.is_file():
            try:
                check_archive(args, input_path, output_prefix)
            except (rarfile.BadRarFile, rarfile.NotRarFile):
                log.info('Corrupt file:', input_path)
            except rarfile.NeedFirstVolume:
                log.debug('NeedFirstVolume', input_path)
            except Exception as e:
                log.exception(input_path)
