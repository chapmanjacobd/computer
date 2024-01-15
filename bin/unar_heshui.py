#!/usr/bin/python3
import argparse
import os
from collections import Counter
from pathlib import Path
import tempfile

import rarfile
from xklb.utils import objects
from xklb.utils.log_utils import log


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unlink", action="store_true")
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
            elif f.filename.lower().endswith(
                ( '.url', '.html', '.htm', '.jpg', '.png', '.bmp', '.gif', '.m3u', 'Thumbs.db', 'desktop.ini', '.DS_Store')
            ):
                continue
            if any(s in f.filename.lower() for s in ('左右反転バージョン',)):
                continue

            files.append(f.filename)

        files, nested_archives = [s for s in files if not s.endswith(('.exe', '.rar', '.zip'))], [
            s for s in files if s.endswith(('.exe', '.rar', '.zip'))
        ]
        if nested_archives:
            log.error('nested archives: %s', nested_archives)
            with tempfile.TemporaryDirectory() as temp_prefix:
                rf.extractall(temp_prefix)
                for nested_archive in nested_archives:
                    temp_path = Path(temp_prefix) / nested_archive
                    try:
                        count_extracted += check_archive(args, temp_path, output_prefix)
                    except (rarfile.BadRarFile, rarfile.NotRarFile):
                        log.info('Corrupt file: %s', temp_path)
                    except rarfile.NeedFirstVolume:
                        log.debug('NeedFirstVolume: %s', temp_path)
                    except Exception:
                        log.exception(input_path)
                        raise
            if not files:
                if args.unlink:
                    input_path.unlink()
                return count_extracted

        extensions = Counter(Path(s).suffix.lower() for s in files)

        for extra in ['.lrc', '.rtf', '.txt', '.pdf', '.docx']:
            if extra in extensions:
                extra_files = [s for s in files if s.endswith(extra)]
                log.info('Extracting %s extras %s', extra, extra_files)
                for member in extra_files:
                    rf.extract(member, output_prefix)
                del extensions[extra]

        if len(files) == 0:
            log.error('No files found in: %s', input_path)
        elif len(extensions) == 1:
            key, _value = extensions.popitem()
            for member in [s for s in files if s.endswith(key)]:
                log.debug('One type of extension: %s', member)
                if not args.dry_run:
                    rf.extract(member, output_prefix)
                count_extracted += 1

            if args.unlink:
                input_path.unlink()
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

                if args.unlink:
                    input_path.unlink()
        else:
            log.error('Directory structure not recognized: %s', files)
    return count_extracted


if __name__ == "__main__":
    args = parse_args()

    src = Path(args.source_path)
    output_prefix = src.parent / (src.parent.name + 'out')
    output_prefix.mkdir(exist_ok=True)  # exist_ok=args.dry_run

    count_skipped = 0
    count_processed = 0
    count_files = 0
    for input_path in src.rglob('*'):
        if input_path.is_file():
            try:
                ar_extracted = check_archive(args, input_path, output_prefix)
                if ar_extracted > 0:
                    count_files += ar_extracted
                    count_processed += 1
                else:
                    count_skipped += 1
            except (rarfile.BadRarFile, rarfile.NotRarFile):
                log.info('Corrupt file: %s', input_path)
            except rarfile.NeedFirstVolume:
                log.debug('NeedFirstVolume: %s', input_path)
            except Exception as e:
                log.exception(input_path)
                if args.dry_run:
                    raise

    print('Skipped:', count_skipped, 'Processed:', count_processed, 'Files:', count_files)
