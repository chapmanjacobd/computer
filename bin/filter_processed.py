#!/usr/bin/python3
import argparse
import os
from subprocess import TimeoutExpired

from library.utils import arggroups, consts, shell_utils, processes


def is_processed(filepath):
    filename = os.path.basename(filepath)
    _, ext = os.path.splitext(filename)
    ext = ext.lower().lstrip('.')

    if ext in ('avif', 'srt', 'vtt'):
        return True
    elif ext in consts.VIDEO_EXTENSIONS | consts.AUDIO_ONLY_EXTENSIONS:
        try:
            probe = processes.FFProbe(filepath)
        except (processes.UnplayableFile, TimeoutExpired):
            return False
        else:
            if probe.has_video:
                for s in probe.video_streams:
                    if s['codec_name'] == 'av1':
                        return True
            else:
                for s in probe.audio_streams:
                    if s['codec_name'] == 'opus':
                        return True

    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("-n", action='store_true')
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser)
    args = parser.parse_args()
    arggroups.args_post(args, parser)

    if args.n:
        args.processed = False

    for p in shell_utils.gen_paths(args):
        if is_processed(p) is args.processed:
            print(p)


if __name__ == "__main__":
    main()
