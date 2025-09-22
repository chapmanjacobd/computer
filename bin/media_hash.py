#!/usr/bin/env python

import base64
import hashlib
import json
import re
import subprocess
import sys


def main():
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-v", "fatal", "-i", sys.argv[1], "-t", "5.", "-f", "framemd5", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout = p.stdout or []

    chans = {}
    for l in stdout:
        if l.startswith(b"#stream#"):
            break

        m = re.match(r"^#media_type ([0-9]): ([a-zA-Z])", l.decode("utf-8"))
        if m:
            chans[m.group(1)] = m.group(2)

    hashers = [hashlib.sha512(), hashlib.sha512()]
    for l in stdout:
        n = int(l[:1])
        v = l.rsplit(b",", 1)[-1].strip()
        hashers[n].update(v)

    r = {}
    for k, v in chans.items():
        dg = hashers[int(k)].digest()[:12]
        dg = base64.urlsafe_b64encode(dg).decode("ascii")
        r[v[0].lower() + "hash"] = dg

    print("".join(r.values()))


if __name__ == "__main__":
    main()
