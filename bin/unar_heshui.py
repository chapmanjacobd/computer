#!/usr/bin/python3
import argparse
import os
import tempfile
import zipfile
from collections import Counter, OrderedDict
from pathlib import Path

import rarfile
from xklb.scripts import process_audio
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


class ArchiveHandler:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.archive = None

    def __enter__(self):
        if self.file_path.suffix == '.zip':
            self.archive = zipfile.ZipFile(self.file_path)
        else:
            self.archive = rarfile.RarFile(self.file_path, errors='strict')
        return self.archive

    def __exit__(self, exc_type, exc_value, traceback):
        if self.archive:
            self.archive.close()


def delete_archive(input_path, rf):
    if isinstance(rf, zipfile.ZipFile):
        input_path.unlink()
    else:
        for s in rf.volumelist():
            os.unlink(s)


def check_archive(args, input_path: Path, output_prefix: Path):
    count_extracted = 0

    output_prefix = output_prefix / input_path.stem
    output_prefix = Path(*OrderedDict.fromkeys(output_prefix.parts).keys())  # remove duplicate path parts

    with ArchiveHandler(input_path) as rf:
        rf.setpassword(b'heshui')

        files = []
        for f in rf.infolist():
            if f.file_size == 0:
                if not f.filename.endswith(os.sep):
                    log.warning('Ignoring non-directory zero size file: %s', f.filename)
                continue
            elif f.filename.lower().endswith(
                (
                    '.url',
                    '.website',
                    '.html',
                    '.htm',
                    '.jpg',
                    '.jpeg',
                    '.png',
                    '.bmp',
                    '.gif',
                    '.m3u',
                    'Thumbs.db',
                    'desktop.ini',
                    '.DS_Store',
                )
            ):
                continue
            if any(s in f.filename.lower() for s in ('左右反転バージョン',)):
                continue

            files.append(f.filename)

        files, nested_archives = [s for s in files if not s.endswith(('.exe', '.rar', '.zip'))], [
            s for s in files if s.endswith(('.exe', '.rar', '.zip'))
        ]
        if nested_archives:
            log.info('nested archives: %s', nested_archives)
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
                    except FileNotFoundError:
                        log.debug('FileNotFoundError: %s', temp_path)
                    except Exception:
                        log.exception(input_path)
                        raise

        extensions = Counter(Path(s).suffix.lower() for s in files)
        for extra in ['.lrc', '.rtf', '.txt', '.pdf', '.docx', '.mp4','.mkv']:
            if extra in extensions:
                extra_files = [s for s in files if s.endswith(extra)]
                log.info('Extracting %s extras %s', extra, extra_files)
                for member in extra_files:
                    if not args.dry_run:
                        rf.extract(member, output_prefix)
                    files.remove(member)
                    count_extracted += 1
                del extensions[extra]

        if nested_archives:
            if not files:
                if args.unlink:
                    delete_archive(input_path, rf)
                return count_extracted

        if len(files) == 0:
            log.error('No files found in: %s', input_path)
            return count_extracted
        elif len(extensions) == 1:
            key, _value = extensions.popitem()
            for member in [s for s in files if s.endswith(key)]:
                log.debug('One type of extension: %s', member)
                if not args.dry_run:
                    output_path = rf.extract(member, output_prefix)
                    process_audio.process_path(output_path)
                count_extracted += 1

            if args.unlink:
                delete_archive(input_path, rf)
        else:  # len(extensions) >= 2

            low_q_exts = ['.mp3', '.wma']
            high_q_exts = ['.wav', '.flac']

            for low_q_ext in low_q_exts:
                for member in [s for s in files if s.lower().endswith(low_q_ext)]:
                    for high_q_ext in high_q_exts:
                        if Path(member).with_suffix(high_q_ext).name in [Path(s).name for s in files]:
                            files.remove(member)

            for member in files:
                if not args.dry_run:
                    output_path = rf.extract(member, output_prefix)
                    process_audio.process_path(output_path)
                count_extracted += 1

        if args.unlink:
            delete_archive(input_path, rf)

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
                log.warning('Corrupt file: %s', input_path)
            except rarfile.NeedFirstVolume:
                log.debug('NeedFirstVolume: %s', input_path)
            except FileNotFoundError:
                log.debug('FileNotFoundError: %s', input_path)
            except Exception as e:
                log.exception(input_path)
                if args.dry_run:
                    raise

    print('Skipped:', count_skipped, 'Processed:', count_processed, 'Files:', count_files)
