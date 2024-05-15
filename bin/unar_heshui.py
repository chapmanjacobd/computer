#!/usr/bin/python3
import argparse
from xklb.utils import argparse_utils
import os
import tempfile
import zipfile
from collections import Counter, OrderedDict
from pathlib import Path

import rarfile
from xklb.mediafiles import process_ffmpeg
from xklb.folders.rel_mv import rel_move
from xklb.utils import objects, arggroups
from xklb.utils.log_utils import log

# fd . -eRAR ASMR-part2/ | parallel --joblog /home/xk/.jobs/joblog_2024-01-17T140222.log --resume-failed -j8 unar_heshui.py --unlink {}

TEMP_BASE_DIR = Path('~/.tmp').expanduser()
TEMP_BASE_DIR.mkdir(exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse_utils.ArgumentParser()
    parser.add_argument("--unlink", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", "-v", action="count", default=0)
    arggroups.process_ffmpeg(parser)

    parser.add_argument("rar_path")
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

def filter_archives(files):
    non_archive_files = [p for p in files if not p.name.endswith(('.exe', '.rar', '.zip'))]
    archive_files = [p for p in files if p.name.endswith(('.exe', '.rar', '.zip'))]

    first_part_archives = []
    for p in archive_files:
        if p.suffix[2:].isdigit() and int(p.suffix[2:]) > 1:
            continue
        elif 'part' in p.stem.split('.')[-1] and p.stem[-1].isdigit() and int(p.stem[-1]) > 1:
            continue

        first_part_archives.append(p)

    return non_archive_files, first_part_archives

def check_archive(args, input_path: Path, output_prefix: Path):
    count_extracted = 0

    output_prefix = output_prefix / input_path.stem
    output_prefix = Path(*OrderedDict.fromkeys(output_prefix.parts).keys())  # remove duplicate path parts

    with ArchiveHandler(input_path) as rf:
        rf.setpassword(b'heshui')

        with tempfile.TemporaryDirectory(dir=TEMP_BASE_DIR) as temp_prefix1:
            rf.extractall(temp_prefix1)

            files = []
            for p in Path(temp_prefix1).rglob('*'):
                if not p.is_file():
                    continue

                stats = p.stat()
                if stats.st_size == 0:
                    log.warning('Ignoring non-directory zero size file: %s', p)
                elif p.name.lower().endswith(
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
                ) or any(s in p.name.lower() for s in ('左右反転バージョン',)):
                    log.debug('Ignoring file: %s', p)
                else:
                    files.append(p)

            files, nested_archives = filter_archives(files)
            if nested_archives:
                log.info('nested archives: %s', nested_archives)
                for nested_archive in nested_archives:
                    temp_path = Path(temp_prefix1) / nested_archive
                    try:
                        count_extracted += check_archive(args, temp_path, output_prefix)
                    except (rarfile.BadRarFile, rarfile.NotRarFile):
                        log.info('Corrupt file: %s', temp_path)
                        args.unlink = False
                    except rarfile.NeedFirstVolume:
                        log.debug('NeedFirstVolume: %s', temp_path)
                    except zipfile.BadZipFile:
                        log.exception('Nested zip: %s', temp_path)
                        args.unlink = False
                    except FileNotFoundError:
                        log.debug('FileNotFoundError: %s', temp_path)
                    except Exception:
                        log.exception(input_path)
                        raise

            extensions = Counter(p.suffix.lower() for p in files)
            for extra in ['.lrc', '.rtf', '.txt', '.pdf', '.docx', '.mp4', '.mkv']:
                if extra in extensions:
                    extra_files = [p for p in files if p.name.endswith(extra)]
                    log.info('Extracting %s extras %s', extra, extra_files)
                    for p in extra_files:
                        rel_move([p], output_prefix, simulate=args.dry_run, relative_from=[temp_prefix1])
                        files.remove(p)
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
            elif len(extensions) > 1:
                low_q_exts = ['.mp3', '.wma', '.aac']
                high_q_exts = ['.wav', '.flac']

                for low_q_ext in low_q_exts:
                    for p in [p for p in files if p.name.lower().endswith(low_q_ext)]:
                        for high_q_ext in high_q_exts:
                            if p.with_suffix(high_q_ext).name in [p.name for p in files]:
                                try:
                                    files.remove(p)
                                except ValueError:
                                    pass

            for p in files:
                if not args.dry_run:
                    try:
                        p = process_ffmpeg.process_path(args, p)
                    except Exception:
                        pass
                rel_move([p], output_prefix, simulate=args.dry_run, relative_from=[temp_prefix1])
                count_extracted += 1

            if args.unlink:
                delete_archive(input_path, rf)

    return count_extracted


if __name__ == "__main__":
    args = parse_args()

    input_path = Path(args.rar_path)

    output_prefix = Path('out').resolve()
    output_prefix.mkdir(exist_ok=True)  # exist_ok=args.dry_run

    try:
        ar_extracted = check_archive(args, input_path, output_prefix)
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
