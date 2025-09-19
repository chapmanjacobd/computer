#!/usr/bin/env python2
# coding: utf-8
from __future__ import print_function, unicode_literals

"""unbork.py: Filename fixer"""
__version__ = "1.2"
__author__ = "ed <irc.rizon.net>"
__license__ = "MIT"
__copyright__ = 2015

import os
import re
import struct
import sys
from urllib.parse import unquote

# python doesn't provide a list of available encodings so here it is
codecs = [
    'ascii',
    'big5',
    'big5hkscs',
    'cp037',
    'cp424',
    'cp437',
    'cp500',
    'cp720',
    'cp737',
    'cp775',
    'cp850',
    'cp852',
    'cp855',
    'cp856',
    'cp857',
    'cp858',
    'cp860',
    'cp861',
    'cp862',
    'cp863',
    'cp864',
    'cp865',
    'cp866',
    'cp869',
    'cp874',
    'cp875',
    'cp932',
    'cp949',
    'cp950',
    'cp1006',
    'cp1026',
    'cp1140',
    'cp1250',
    'cp1251',
    'cp1252',
    'cp1253',
    'cp1254',
    'cp1255',
    'cp1256',
    'cp1257',
    'cp1258',
    'euc_jp',
    'euc_jis_2004',
    'euc_jisx0213',
    'euc_kr',
    'gb2312',
    'gbk',
    'gb18030',
    'hz',
    'iso2022_jp',
    'iso2022_jp_1',
    'iso2022_jp_2',
    'iso2022_jp_2004',
    'iso2022_jp_3',
    'iso2022_jp_ext',
    'iso2022_kr',
    'latin_1',
    'iso8859_2',
    'iso8859_3',
    'iso8859_4',
    'iso8859_5',
    'iso8859_6',
    'iso8859_7',
    'iso8859_8',
    'iso8859_9',
    'iso8859_10',
    'iso8859_11',
    'iso8859_13',
    'iso8859_14',
    'iso8859_15',
    'iso8859_16',
    'johab',
    'koi8_r',
    'koi8_u',
    'mac_cyrillic',
    'mac_greek',
    'mac_iceland',
    'mac_latin2',
    'mac_roman',
    'mac_turkish',
    'ptcp154',
    'shift_jis',
    'shift_jis_2004',
    'shift_jisx0213',
    'utf_32',
    'utf_32_be',
    'utf_32_le',
    'utf_16',
    'utf_16_be',
    'utf_16_le',
    'utf_7',
    'utf_8',
    'utf_8_sig',
]


def eprint(*args, **kwargs):
    kwargs["file"] = sys.stderr
    print(*args, **kwargs)
    sys.stderr.flush()  # ???


# Cross-platform (doubt.jpg) read single key
try:
    from msvcrt import getch
except:
    import termios
    import tty

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class Config:
    mode = None
    via = None


def enum(**enums):
    return type(str("Enum"), (), enums)


Modes = enum(URL=1, VIA=2)


def sanitize(txt, for_print=True):
    """strip unprintables"""
    pre = suf = ""
    if for_print:
        pre = "\x1b[1;31m"
        suf = "\x1b[0m"

    f = chr

    bads = {}
    for r in [range(0, 32), range(127, 160)]:
        for n in r:
            bads[f(n)] = "<{0:02x}>".format(n)

    ret = ""
    for ch in txt:
        if ch in bads:
            ret += pre + bads[ch] + suf
        else:
            ret += ch

    return ret


cfg = Config()

# Check if mode 1 (url)
if len(sys.argv) == 2 and sys.argv[1] == "url":
    cfg.mode = Modes.URL

# Check if mode 2 (via)
elif len(sys.argv) == 4 and sys.argv[2] == "via":
    cfg.mode = Modes.VIA
    enc = sys.argv[1]
    via = sys.argv[3]
    cs = b""
    for a in range(128, 255):
        cs += struct.pack(b"B", a)
    cs = cs.decode(via)
    cs = "([" + cs + "]{3}|(?:[" + cs + "].){2})"
    cfg.via = re.compile(cs, flags=re.U)
    # eprint(cs)

# Check if mode 3 (detect)
elif len(sys.argv) == 4 and sys.argv[1] == "find":
    hits = 0
    bad = sys.argv[2]
    good = sys.argv[3]
    # eprint(repr(bad))
    # sys.exit(0)

    for via in codecs:
        try:
            tmp = bad.encode(via)
        except:
            continue

        for enc in codecs:
            try:
                tmp2 = tmp.decode(enc)
                if tmp2 != good:
                    continue
            except:
                continue

            hits += 1
            eprint(
                "%s \x1b[1;31m%s\x1b[0m via \x1b[1;32m%s\x1b[0m"
                % (
                    sys.argv[0],
                    enc,
                    via,
                )
            )

    eprint("Detection complete, found %d possible fixes" % (hits,))
    sys.exit(0)

else:
    eprint(
        """
\x1b[0;33mUsage:\x1b[0m
   unbork.py url
   unbork.py ENCODING via ENCODING
   unbork.by find 'BROKEN' 'GOOD'

\x1b[0;33mExample 1:\x1b[0m
   URL-escaped UTF-8, looks like this in ls:
   ?%81%8b?%81%88?%82%8a?%81??%81%a1.mp3

   \x1b[33m{0}\033[0;1m url\x1b[0m
   (\x1b[1;31m81%8b81%8882%8a81▒81%a1.mp3\x1b[0m) => (\x1b[1;32mかえりみち.mp3\x1b[0m)

\x1b[0;33mExample 2:\x1b[0m
   SJIS (cp932) parsed as MSDOS (cp437) looks like...
   ëFæ╜ôcâqâJâï - ì≈ù¼é╡.mp3

   \x1b[33m{0}\033[0;1m cp932 via cp437\x1b[0m
   (\x1b[1;31mëFæ╜ôcâqâJâï - ì≈ù¼é╡.mp3\x1b[0m) => (\x1b[1;32m宇多田ヒカル - 桜流し.mp3\x1b[0m)

\x1b[0;33mExample 3:\x1b[0m
   Find a correction method from BROKEN to GOOD

   \x1b[33m{0}\033[0;1m find 'УпРlЙ╣Кy' '同人音楽'\x1b[0m
      .../unbork.py \x1b[1;31mcp932\x1b[0m via \x1b[1;32mcp866\x1b[0m ...
      Detection complete, found 4 possible fixes
""".format(
            sys.argv[0],
        )
    )
    sys.exit(1)


def rename(cfg, folder):
    """Iterate through a folder and find files to rename"""
    for name in os.listdir(folder):
        if cfg.mode == Modes.URL:
            fixed = unquote(name.decode("utf-8", "ignore")).encode("utf-8")

        elif cfg.mode == Modes.VIA:
            try:
                bork8 = name.decode("utf-8")
                if not cfg.via.search(bork8):
                    continue

                fixed = bork8.encode(via).decode(enc).encode("utf-8")
            except Exception as e:
                continue
        else:
            raise Exception("Unknown conversion mode [%s]" % cfg.mode)

        if fixed == name:
            continue

        msg = "({0}) => (\x1b[1;32m{1}\x1b[0m) ".format(
            sanitize(name.decode("utf-8", "replace")), sanitize(fixed.decode("utf-8"))
        )
        eprint(msg, end="")
        ch = getch()
        eprint(ch)
        if ch == "y":
            path_from = os.path.join(folder, name)
            path_to = os.path.join(folder, fixed)
            os.rename(path_from, path_to)
        if ch == "q":
            sys.exit(0)


def iterate(cfg, folder):
    """Recursively traverse a folder"""
    rename(cfg, folder)
    for subfolder in os.listdir(folder):
        path = os.path.join(folder, subfolder)
        if os.path.isdir(path):
            eprint("Entering [{0}]".format(sanitize(path.decode("utf-8", "replace"))))
            iterate(cfg, path)


eprint("\nListing files. For each file, select [Y]es [N]o [Q]uit.\n")
iterate(cfg, b".")
eprint("done")


# url (bad testcase, find a better one)
# echo h > '%E3%81%8B%E3%81%88%E3%82%8A%E3%81%BF%E3%81%A1.mp3'
#
# sjis via latin1
# echo h > "$(echo ごみ箱 | iconv -t sjis | iconv -f latin1)"
