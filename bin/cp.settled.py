#!/usr/bin/env python3
from __future__ import print_function, unicode_literals

VERSION = "1.3"

"""
migratory - data conveyor
2018, ed <irc.rizon.net>, MIT-licensed, https://github.com/9001/usr-local-bin

monitors a source folder for new files to become stable (no changes to either
the filesize or last-modified timestamp for a given period of time) and then
either copies or moves the file to the destination folder

runs in python 3.6 and later by default,
but if you really need 2.6 or 2.7 support:

from strip_hints import strip_file_to_string
with open("migratory26.py","wb") as f:
  s=strip_file_to_string("/usr/local/bin/migratory",no_ast=True,to_empty=True)
  f.write(s.encode("utf-8"))
"""

import datetime
import hashlib
import logging
import os
import platform
import re
import shutil
import stat
import sys
import time

try:
    from typing import Generator, List, Optional, Pattern, Tuple
except:
    pass

try:
    import argparse
except:
    m = "\n  ERROR: need 'argparse'; download it here:\n   https://github.com/ThomasWaldmann/argparse/raw/master/argparse.py\n"
    print(m)
    raise


PY2 = sys.version_info < (3,)
WINDOWS = platform.system() == "Windows"
ANYWIN = WINDOWS or sys.platform in ["msys", "cygwin"]
Hasher = None
if PY2:
    bytes = str
else:
    unicode = str


try:
    UTC = datetime.timezone.utc
except:
    TD_ZERO = datetime.timedelta(0)

    class _UTC(datetime.tzinfo):
        def utcoffset(self, dt):
            return TD_ZERO

        def tzname(self, dt):
            return "UTC"

        def dst(self, dt):
            return TD_ZERO

    UTC = _UTC()


logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
warn = logger.warning
error = logger.error


class LoggerFmt(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.DEBUG:
            ansi = "\033[01;30m"
        elif record.levelno == logging.INFO:
            ansi = "\033[0;32m"
        elif record.levelno == logging.WARN:
            ansi = "\033[0;33m"
        else:
            ansi = "\033[01;31m"

        zd = datetime.datetime.fromtimestamp(record.created)
        ts = "%04d-%02d-%02d %02d:%02d:%02d.%03d" % (
            zd.year,
            zd.month,
            zd.day,
            zd.hour,
            zd.minute,
            zd.second,
            zd.microsecond // 1000,
        )

        msg = record.msg
        if record.args:
            msg = msg % record.args

        return "\033[0;36m%s%s %s\033[0m" % (ts, ansi, msg)


def init_logger(debug: bool, quiet: bool):
    if WINDOWS:
        os.system("rem")  # enable colors

    lv = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=lv,
        format="\033[36m%(asctime)s.%(msecs)03d\033[0m %(message)s",
        datefmt="%H%M%S",
    )
    lh = logging.StreamHandler(sys.stderr)
    lh.setFormatter(LoggerFmt())
    logging.root.handlers = []
    logger.handlers = [] if quiet else [lh]
    logger.setLevel(lv)


def unix2iso(unix_ts: int) -> str:
    if unix_ts:
        zd = datetime.datetime.fromtimestamp(unix_ts, UTC)
    else:
        zd = datetime.datetime.now(UTC)

    return "%04d-%02d-%02d %02d:%02d:%02d" % (
        zd.year,
        zd.month,
        zd.day,
        zd.hour,
        zd.minute,
        zd.second,
    )


def _scandir(
    err: List[Tuple[str, str]], top: str
) -> Generator[Tuple[str, os.stat_result], None, None]:
    """fast modern approach to non-recursive directory listing with stat() info"""
    with os.scandir(top) as dh:
        for fh in dh:
            abspath = os.path.join(top, fh.name)
            try:
                yield (abspath, fh.stat())
            except Exception as ex:
                err.append((abspath, str(ex)))


def _listdir(
    err: List[Tuple[str, str]], top: str
) -> Generator[Tuple[str, os.stat_result], None, None]:
    """slow fallback approach to non-recursive directory listing with stat() info"""
    for name in os.listdir(top):
        abspath = os.path.join(top, name)
        try:
            yield (abspath, os.stat(abspath))
        except Exception as ex:
            err.append((abspath, str(ex)))


# choose the best directory listing approach
if hasattr(os, "scandir") and sys.version_info > (3, 6):
    statdir = _scandir
else:
    statdir = _listdir


def walkdir(
    err: List[Tuple[str, str]], top: str, seen: List[str]
) -> Generator[Tuple[str, os.stat_result], None, None]:
    """recursive statdir"""
    atop = os.path.abspath(os.path.realpath(top))
    if atop in seen:
        err.append((top, "recursive-symlink"))
        return

    seen = seen[:] + [atop]
    for ap, st in sorted(statdir(err, top)):
        yield ap, st
        if stat.S_ISDIR(st.st_mode):
            try:
                for x in walkdir(err, ap, seen):
                    yield x
            except Exception as ex:
                err.append((ap, str(ex)))


def copystat(src: str, dst: str) -> None:
    try:
        shutil.copystat(src, dst)
    except:
        pass


def hashfile(ap: str) -> str:
    h = Hasher()
    with open(ap, "rb", 1024 * 512) as f:
        while True:
            buf = f.read(1024 * 64)
            if not buf:
                return h.hexdigest()
            h.update(buf)


def copyfile(src: str, dst: str) -> Tuple[str, float]:
    h = Hasher()
    t0 = time.time()
    with open(src, "rb", 1024 * 512) as fi, open(dst, "wb", 1024 * 512) as fo:
        while True:
            buf = fi.read(1024 * 64)
            if not buf:
                break
            fo.write(buf)
            h.update(buf)
    copystat(src, dst)
    return h.hexdigest(), time.time() - t0


class Dirmon(object):
    def __init__(
        self,
        src: str,
        dst: str,
        keep_src: bool,
        log: List[str],
        sf1: List[str],
        sf2: List[str],
        debounce: float,
        dir_linger: float,
        no_atomic: bool,
        keep_ptn: Optional[Pattern],
        ign_ptn: Optional[Pattern],
    ):
        self.src = src  # abspath to monitor / read from
        self.dst = dst  # abspath to copy/move files to
        self.keep = keep_src  # True=copy, False=move
        self.log = log  # file(s) to write transfer log to
        self.statefile1 = sf1  # file(s) to log names of pending/busy files to
        self.statefile2 = sf2  # file(s) to touch when going idle after a transfer
        self.debounce = debounce  # how long a file must remain stable before acting
        self.dir_linger = dir_linger  # how long to keep each empty dir in src
        self.no_atomic = no_atomic  # disable atomic moves; use copy+delete
        self.keep_ptn = keep_ptn  # regex of files/folders to never delete
        self.ign_ptn = ign_ptn  # regex of files/folders to ignore in src

        # abspath => (unix-time, (mtime, filesize));
        # files which have recently appeared and are pending transfer;
        # most recent unix-time when the inode-attrs (mtime,size) changed
        self.known_files: dict[str, Tuple[float, Tuple[float, int]]] = {}

        # abspath => (mtime, filesize);
        # files which have already been copied to dst
        self.kept_files: dict[str, Tuple[float, int]] = {}

        # abspath => unix-time;
        # potentially empty directories to try removing from src
        self.empty_dirs: dict[str, float] = {}

        # relpaths of files which have already been ignored
        self.ignored_files: set[str] = set()

        self.kept_dirs: set[str] = set()  # empty folders kept by --kept
        self.msg_scanning = 0  # time last logged

    def check_once(self):
        now = time.time()
        if now - self.msg_scanning >= 180:
            self.msg_scanning = now
            debug("scanning...")
        err = []
        log = []
        do_log = bool(self.log)
        now = time.time()
        nonempty_dirs = set()
        maybe_empty_dirs = set()
        base_src_ap = self.src + os.sep  # fence (stay in this folder)

        # scan through every (abspath,stat) below src
        num_new = 0
        for ap, st in walkdir(err, self.src, []):
            if not ap.startswith(base_src_ap):
                warn("bailing from symlink into %s", ap)
                continue
            if stat.S_ISDIR(st.st_mode):
                maybe_empty_dirs.add(ap)
                continue
            nonempty_dirs.add(os.path.dirname(ap))
            relpath = ap[len(base_src_ap) :]
            if not stat.S_ISREG(st.st_mode):
                if relpath not in self.ignored_files:
                    self.ignored_files.add(relpath)
                    debug("ignoring non-regular file %s", ap)
                continue
            if self.ign_ptn and self.ign_ptn.match(relpath):
                if relpath not in self.ignored_files:
                    self.ignored_files.add(relpath)
                    debug("file ignored by pattern: %s", relpath)
                continue
            mt_and_sz = (st.st_mtime, st.st_size)
            known = self.known_files.get(ap)
            if (not known) or known[1] != mt_and_sz:
                if not known:
                    num_new += 1
                self.known_files[ap] = (now, mt_and_sz)
                debug("file changed: %s", ap)

        for txt in err:
            warn("read-error: %r", txt)
            if do_log:
                log.append("READ-ERROR: %r" % (txt,))

        if num_new:
            info("spotted %d new files", num_new)

        # build list of currently empty dirs
        if self.keep_ptn:
            for ap in list(maybe_empty_dirs):
                if ap in self.empty_dirs:
                    continue
                relpath = ap[len(base_src_ap) :]
                if self.keep_ptn.match(relpath):
                    nonempty_dirs.add(ap)
                    if ap not in self.kept_dirs:
                        self.kept_dirs.add(ap)
                        debug("folder kept by pattern: %s", relpath)
        for ap in list(nonempty_dirs):
            while len(ap) >= len(base_src_ap):
                maybe_empty_dirs.discard(ap)
                self.empty_dirs.pop(ap, None)
                ap = ap.rsplit(os.sep, 1)[0]
        for ap in list(maybe_empty_dirs):
            if ap not in self.empty_dirs:
                self.empty_dirs[ap] = now
                debug("found empty directory %s", ap)

        # debug("%d known_files, %d empty_dirs", len(self.known_files), len(self.empty_dirs))

        ready = []
        not_ready = []
        for src_ap, (ts, mt_and_sz) in self.known_files.items():
            if now - ts < self.debounce:
                remains = self.debounce - (now - ts)
                debug("waiting %.1fs for %s", remains, src_ap)
                not_ready.append(src_ap)
                continue

            if self.kept_files.get(src_ap) == mt_and_sz:
                continue  # not modified since last copy; skip

            ready.append(src_ap)

        if self.statefile1:
            # write list of busy files
            ready.sort()
            not_ready.sort()
            txt = "# %d files are being transferred to destination:\n%s\n\n# %d pending busy files in source folder:\n%s\n\n"
            txt = txt % (
                len(ready),
                "\n".join([x[len(base_src_ap) :] for x in ready]),
                len(not_ready),
                "\n".join([x[len(base_src_ap) :] for x in not_ready]),
            )
            buf = txt.encode("utf-8", "replace")
            for ap in self.statefile1:
                try:
                    with open(ap, "rb") as f:
                        if f.read() == buf:
                            continue
                except:
                    pass
                with open(ap, "wb") as f:
                    f.write(buf)

        dgst = ""
        for src_ap in ready:
            ts, (f_mt, f_sz) = self.known_files[src_ap]
            dst_ap = os.path.join(self.dst, src_ap[len(base_src_ap) :])
            try:
                debug("file ready for transfer: %s", src_ap)

                # check if target file already exists:
                try:
                    dst_dgst = hashfile(dst_ap)  # keep first so it fails early
                    src_dgst = hashfile(src_ap)
                except:
                    dst_dgst = "x"
                    src_dgst = ""
                if src_dgst == dst_dgst:
                    info("target exists with same contents; skipping %s", src_ap)
                    self.kept_files[src_ap] = (f_mt, f_sz)
                    copystat(src_ap, dst_ap)
                    if not self.keep:
                        os.unlink(src_ap)
                        del self.known_files[src_ap]
                        del self.kept_files[src_ap]
                    continue
                elif src_dgst:
                    t = "new src has different data; src=%s, dst=%s, replacing %s"
                    info(t, src_dgst[:32], dst_dgst[:32], dst_ap)
                    os.unlink(dst_ap)

                # check if need to make target folder:
                mkdir = False
                try:
                    dst_dir = os.path.dirname(dst_ap)
                    dir_st = os.stat(dst_dir)
                    if not stat.S_ISDIR(dir_st.st_mode):
                        t = "target directory name occupied by a file; deleting %s"
                        warn(t, dst_dir)
                        os.unlink(dst_dir)
                        mkdir = True
                except:
                    mkdir = True  # not exist
                if mkdir:
                    debug("mkdir %s", dst_dir)
                    os.makedirs(dst_dir)

                # check if copy or move:
                keep = self.keep
                relpath = src_ap[len(base_src_ap) :]
                if not keep and self.keep_ptn and self.keep_ptn.match(relpath):
                    debug("file kept by pattern: %s", relpath)
                    keep = True

                action_text = "copy" if keep else "move"
                info("%s [%s] to [%s] ...", action_text, src_ap, dst_ap)
                if keep:
                    # mode=copy
                    if os.path.exists(dst_ap):
                        warn("target file exists; deleting %s", dst_ap)
                        os.unlink(dst_ap)
                    self.kept_files[src_ap] = (f_mt, f_sz)
                    dgst, dur = copyfile(src_ap, dst_ap)
                    shutil.copy2(src_ap, dst_ap)
                else:
                    # mode=move
                    try:
                        if self.no_atomic:
                            raise Exception()
                        os.replace(src_ap, dst_ap)
                        dgst = hashfile(dst_ap)
                        dur = 0
                    except:
                        debug("atomic move failed; doing cp+rm instead")
                        if os.path.exists(dst_ap):
                            warn("target file exists; deleting %s", dst_ap)
                            os.unlink(dst_ap)
                        dgst, dur = copyfile(src_ap, dst_ap)
                        os.unlink(src_ap)
                    del self.known_files[src_ap]
                    if not self.dir_linger:
                        try:
                            os.rmdir(os.path.dirname(src_ap))
                        except:
                            pass
                if dur:
                    t = "%s  %s  # %s OK in %.1fs, %dM/s"
                    spd = f_sz / 1024 / 1024 / dur
                    info(t, dgst[:32], dst_ap, action_text, dur, spd)
                else:
                    t = "%s  %s  # %s OK in %.1fs"
                    info(t, dgst[:32], dst_ap, action_text, dur)

                if do_log:
                    dt_now = unix2iso(0)
                    dt_file = unix2iso(f_mt)
                    t = "%s | %s | %12s | %s | %s"
                    log.append(t % (dt_now, dt_file, f_sz, dgst, relpath))

                self.msg_scanning = 0

            except Exception as ex:
                warn("%s [%s] to [%s] failed; %r", action_text, src_ap, dst_ap, ex)
                # in case file disappeared during debounce:
                self.known_files.pop(src_ap, None)

        while True:
            num_dropped = 0
            expired = [
                ap for ap, ts in self.empty_dirs.items() if now > ts + self.dir_linger
            ]
            expired.sort(reverse=True)
            for ap in expired:
                self.empty_dirs.pop(ap, None)
                try:
                    os.rmdir(ap)
                    num_dropped += 1
                    debug("deleted directory %s", ap)
                except Exception as ex:
                    debug("failed to delete directory %s: %r", ap, ex)
            if not num_dropped:
                break

        forget = [x for x in self.kept_files if x not in self.known_files]
        for ap in forget:
            info("file disappeared from src; forgetting %s", ap)
            del self.kept_files[ap]

        if do_log and dgst:
            log_hdr = "\n%19s | %19s | %12s | %s | %s\n" % (
                "action-performed",
                "file-last-modified",
                "file-size",
                "file-digest".rjust(len(dgst)),
                "file-relpath",
            )
            log_entry = (log_hdr + "\n".join(log) + "\n").encode("utf-8", "replace")
            for logfile in self.log:
                with open(logfile, "ab+") as f:
                    f.write(log_entry)

        if self.statefile2 and dgst:
            # write timestamp to indicate activity
            now = ("%.3f\n" % (time.time(),)).encode("utf-8")
            for ap in self.statefile2:
                with open(ap, "wb") as f:
                    f.write(now)

    def run(self, interval, quant):
        while True:
            self.check_once()
            if not quant:
                time.sleep(interval)
                continue
            now = time.time()
            tgt = int(now + interval + 0.8)
            time.sleep(tgt - now)


class APF(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


def main():
    global Hasher

    init_logger("--debug" in sys.argv, "--quiet" in sys.argv)

    info("migratory v%s", VERSION)
    if "--version" in sys.argv:
        return

    for alg in (
        "sha1",  # 0.34s
        "sha512",  # 0.46s
        "blake2b",  # 0.42s
        "sha3_512",  # 1.37s
    ):
        try:
            Hasher = getattr(hashlib, alg, None)
            Hasher(b"a").hexdigest()
            break
        except:
            pass
    info("using %s as file hasher", Hasher)

    # args which accept one or more path (semicolon-separated)
    multipath = "vlog log sf1 sf2".split()

    # fmt: off
    desc = "migratory (data conveyor) v" + VERSION + " - https://youtu.be/bI7U-b7ncYw"
    usage = "see -h / --help" if len(sys.argv) < 2 else None
    ap = argparse.ArgumentParser(
        formatter_class=APF, description=desc, usage=usage,
        epilog="these args take a semicolon-separated list of PATHs: --%s\n " % (" --".join(multipath)),
    )
    ap.add_argument("--src", type=unicode, metavar="PATH", required=True, help="source folder to monitor")
    ap.add_argument("--dst", type=unicode, metavar="PATH", required=True, help="destination folder to write into")
    ap.add_argument("--mv", action="store_true", help="move (instead of copy) from SRC to DST")
    ap.add_argument("--debug", action="store_true", help="what bugs? :^)")
    ap.add_argument("--quiet", action="store_true", help="don't log to stdout")
    ap.add_argument("--vlog", type=unicode, metavar="PATH", default="", help="log diagnostics to textfile at PATH")
    ap.add_argument("--log", type=unicode, metavar="PATH", default="", help="write transfer-log to textfile at PATH")
    ap.add_argument("--sf1", type=unicode, metavar="PATH", default="", help="list unstable/pending source files to PATH")
    ap.add_argument("--sf2", type=unicode, metavar="PATH", default="", help="write unixtime to PATH when going idle after a transfer")
    ap.add_argument("--rate", type=float, metavar="SEC", default=1, help="how often to scan SRC for changes")
    ap.add_argument("--wait", type=float, metavar="SEC", default=7, help="how long to wait for a file to settle; 0 is very dangerous")
    ap.add_argument("--edir", type=float, metavar="SEC", default=69, help="how long to keep empty folders in SRC; 0 removes immediately")
    ap.add_argument("--keep", type=unicode, metavar="RE", default="", help="regex (relative to SRC) of files/folders to never delete; dirsep is /")
    ap.add_argument("--ignore", type=unicode, metavar="RE", default="", help="regex (relative to SRC) of files/folders to ignore in src")
    ap.add_argument("--noatomic", action="store_true", help="disable atomic moves; use copy+delete instead")
    ap.add_argument("--quant", action="store_true", help="quantize scans to start at whole seconds")
    ap.add_argument("--version", action="store_true", help="show version and exit")
    # fmt: on

    ar = ap.parse_args()
    src = os.path.abspath(os.path.realpath(ar.src))
    dst = os.path.abspath(os.path.realpath(ar.dst))
    keep = re.compile(ar.keep) if ar.keep else None
    ignore = re.compile(ar.ignore) if ar.ignore else None

    # expand semicolon-separated values into lists
    for name in multipath:
        value = getattr(ar, name)
        values = [x.strip() for x in (value.split(";") if value else [])]
        setattr(ar, name, values)

    for logfile in ar.vlog:
        lh = logging.FileHandler(logfile, "a+", encoding="utf-8", errors="replace")
        lh.setFormatter(LoggerFmt())
        logger.handlers.append(lh)

    info("SRC (monitoring): %s", src)
    info("DST (output-dir): %s", dst)
    info("will %s files from SRC into DST", "MOVE" if ar.mv else "COPY")

    t = "there %s exceptions for specific files/folders to entirely ignore in the source directory"
    info(t, "ARE" if ar.ignore else "are NO")

    if ar.mv:
        t = "there %s exceptions for specific files/folders to always keep present in the source directory"
        info(t, "ARE" if ar.keep else "are NO")

    t = "will scan every %.1f seconds, waiting until each file in SRC is idle for at least %.1f sec, and keeping empty folders in SRC for %.1f sec"
    info(t, ar.rate, ar.wait, ar.edir)

    mon = Dirmon(
        src=src,
        dst=dst,
        keep_src=not ar.mv,
        log=ar.log,
        sf1=ar.sf1,
        sf2=ar.sf2,
        debounce=ar.wait,
        dir_linger=ar.edir,
        no_atomic=ar.noatomic,
        keep_ptn=keep,
        ign_ptn=ignore,
    )
    mon.run(ar.rate, ar.quant)


if __name__ == "__main__":
    main()
