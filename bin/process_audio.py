#!/usr/bin/python3
import argparse
import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import List

parser = argparse.ArgumentParser()
parser.add_argument('paths', nargs='+')
args = parser.parse_args()

for path in args.paths:
    path = str(Path(path).resolve())

    ffprobe_cmd = ['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', path]
    result = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    info = json.loads(result.stdout)

    channels = info['streams'][0]['channels']
    bitrate = int(info['format']['bit_rate'])
    source_rate = int(info['streams'][0]['sample_rate'])
    duration = float(info['format']['duration'])

    assert bitrate > 0
    assert channels > 0
    assert source_rate > 0

    ff_opts: List[str] = []
    if channels == 1:
        ff_opts.extend(['-ac 1'])
    else:
        ff_opts.extend(['-ac 2'])

    if bitrate >= 256000:
        ff_opts.extend(['-b:a 128k'])
    else:
        ff_opts.extend(['-b:a 64k', '-frame_duration 40'])

    if source_rate >= 44100:
        opus_rate = 48000
    elif source_rate >= 22050:
        opus_rate = 24000
    else:
        opus_rate = 16000
    ff_opts.extend([f"-ar {opus_rate}"])

    new_path = str(Path(path).with_suffix('.opus'))

    cmd = f'ffmpeg -nostdin -hide_banner -loglevel warning -y -i {shlex.quote(path)} -c:a libopus {" ".join(ff_opts)} -vbr constrained -filter:a loudnorm=i=-18:lra=17 {shlex.quote(new_path)}'
    subprocess.check_call(cmd, shell=True)

    os.remove(path)  # Remove original

    if duration > 2200:
        cmd = f"split_by_silence.sh {shlex.quote(new_path)} {shlex.quote(str(Path(new_path).with_suffix('.%03d.opus')))}"
        subprocess.run(cmd, shell=True)
