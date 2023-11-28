#!/usr/bin/python3
import argparse
import os
from collections import Counter
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
    count_extracted = 0
    with rarfile.RarFile(input_path, errors='strict') as rf:
        rf.setpassword('heshui')

        files = []
        for f in rf.infolist():
            if f.file_size == 0:
                if not f.filename.endswith(os.sep):
                    log.warning('Ignoring non-directory zero size file: %s', f.filename)
                continue
            elif f.filename.lower().endswith(('.txt', '.pdf', '.docx', '.url', '.html', '.htm', '.jpg', '.png', '.bmp', '.gif', '.m3u', 'Thumbs.db')):
                continue

            files.append(f.filename)

        files, nested_archives = [s for s in files if not s.endswith(('.exe', '.rar'))], [s for s in files if s.endswith(('.exe', '.rar'))]
        if nested_archives:
            log.error('nested archives: %s', nested_archives)

        extensions = Counter(Path(s).suffix.lower() for s in files)

        if len(files) == 0:
            log.error('No files found in: %s', input_path)
        elif len(extensions) == 1:
            for member in files:
                log.debug('One type of extension: %s', member)
                if not args.dry_run:
                    rf.extract(member, output_prefix)
                count_extracted += 1
        elif len(extensions) == 2:
            fist_ext, second_ext = extensions

            low_q_ext, high_q_ext = None, None
            if len([s for s in files if s.endswith(fist_ext)]) != len([s for s in files if s.endswith(second_ext)]):
                log.error('Mismatched extensions %s: %s', extensions, files)
            elif set(extensions) == {'.mp3', '.wav'}:
                low_q_ext, high_q_ext = '.mp3', '.wav'
            elif set(extensions) == {'.mp3', '.flac'}:
                low_q_ext, high_q_ext = '.mp3', '.flac'
            else:
                log.error('Two extension structure %s not recognized: %s', extensions, files)

            if low_q_ext and high_q_ext:
                for member in [s for s in files if s.endswith(high_q_ext)]:
                    log.debug('%s and %s: %s', low_q_ext, high_q_ext, member)
                    if not args.dry_run:
                        rf.extract(member, output_prefix)
                    count_extracted += 1
        else:
            log.error('Directory structure not recognized: %s', files)
    return count_extracted


if __name__ == "__main__":
    args = parse_args()

    src = args.source_path
    output_prefix = src.parent / (src.parent.name + '_out')
    output_prefix.mkdir(exist_ok=args.dry_run)

    count_skipped=0
    count_processed=0
    count_files=0
    for input_path in src.rglob('*'):
        if input_path.is_file():
            try:
                ar_extracted = check_archive(args, input_path, output_prefix)
                if ar_extracted > 0:
                    count_processed += 1
                    count_files += check_archive(args, input_path, output_prefix)
                else:
                    count_skipped += 1
            except (rarfile.BadRarFile, rarfile.NotRarFile):
                log.info('Corrupt file: %s', input_path)
            except rarfile.NeedFirstVolume:
                log.debug('NeedFirstVolume: %s', input_path)
            except Exception as e:
                log.exception(input_path)

    print('Skipped:',  count_processed, 'Processed:',  count_processed, 'Files:', count_files)
