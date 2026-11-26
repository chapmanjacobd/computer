#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["textual>=1.0"]
# ///
# SPDX-License-Identifier: WTFPL
"""procwatch - process baseline and anomaly dashboard.

procwatch samples /proc, records a per-command baseline in SQLite under the
XDG state directory, and highlights processes that are new, rare, returning,
or behaving unlike their baseline. The main view groups processes by what they
are doing (serving, connecting, writing, computing, ...). The all-processes
view sorts on connections, privilege/capability score, write rate, network
transmit rate, CPU, memory, age, or novelty. Additional views aggregate
commands and cgroups, list network endpoints, and show risky processes.

Files (all XDG):
  $XDG_STATE_HOME/procwatch/baseline.db      baseline + events (default
                                             ~/.local/state/procwatch)
  $XDG_CONFIG_HOME/procwatch/config.toml     optional thresholds
  $XDG_CACHE_HOME/procwatch/                 reserved
  $XDG_RUNTIME_DIR/procwatch.lock            single-writer lock

Run:
  ./procwatch.py                 TUI (uses uv to provide textual)
  ./procwatch.py --snapshot      grouped text snapshot, then exit
  ./procwatch.py --snapshot --json
  ./procwatch.py --baseline      baseline statistics
  ./procwatch.py --reset-baseline
  ./procwatch.py --events
  ./procwatch.py -v              debug logging to the XDG state log

Keys in the TUI:
  1/2/3       triage / all processes / events
  4/5/6       commands / network sockets / cgroups
  7 or !      risk (root, dangerous caps, deleted exe, suspicious path)
  j/k, g/G    move, top, bottom
  left/right  scroll one column
  [ / ]       previous / next group (triage)
  s/S         cycle sort column / reverse
  click       sort by a column (all-processes and risk views)
  n           cycle novelty filter (all, NEW, CHANGED, RARE, RETURNING)
  t           toggle process tree (all-processes view)
  w           toggle compact / wide columns
  enter       full scrollable detail screen
  y           copy selected pid/command
  /           filter by pid, name, user, category, capability
  r           refresh now (auto-refresh is off by default)
  R           toggle auto-refresh
  +/-         adjust auto-refresh interval
  ?           full keyboard shortcut list
  q           quit

Network byte counters come from `ss -tinp` when available; socket counts come
from /proc/<pid>/fd + /proc/net/* (procwatch's network namespace only). Running
as root gives complete data for other users' processes; otherwise restricted
fields are shown as zero.

Optional config keys (all thresholds):
  interval = 2.0
  write_rate_mb = 1
  read_rate_mb = 4
  cpu_percent = 25
  rare_observations = 3
  dormant_days = 7
  history_days = 14
  warm_identities = 50
  event_dedupe_seconds = 3600
  suspicious_paths = ["/tmp/", "/var/tmp/", "/dev/shm/"]

Tests:
  python3 -m pytest -q procwatch_tests.py
  uv run --no-project --with 'textual>=8' --with pytest pytest -q procwatch_tests.py
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import fcntl
import hashlib
import json
import logging
import logging.handlers
import os
import pwd
import re
import shutil
import socket as socketlib
import sqlite3
import subprocess
import sys
import time
import tomllib
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Self

__version__ = "0.1.0"

LOG = logging.getLogger("procwatch")

VIEWS = ("main", "all", "events", "commands", "network", "cgroups", "risk")
VIEW_LABELS = {
    "main": "Triage",
    "all": "All processes",
    "events": "Events",
    "commands": "Commands",
    "network": "Network",
    "cgroups": "Cgroups",
    "risk": "Risk",
}
NOVELTY_FILTERS = ("", "NEW", "CHANGED", "RARE", "RETURNING")
SORT_KEYS = (
    "connections",
    "perm",
    "write",
    "tx",
    "cpu",
    "mem",
    "novelty",
    "age",
    "name",
    "pid",
)
SORT_LABELS = {
    "connections": "CONN",
    "perm": "PERM",
    "write": "WR/s",
    "tx": "TX/s",
    "cpu": "CPU",
    "mem": "MEM",
    "novelty": "NOV",
    "age": "AGE",
    "name": "NAME",
    "pid": "PID",
}
CATEGORY_ORDER = (
    "servers",
    "clients",
    "writers",
    "compute",
    "interactive",
    "daemons",
    "idle",
    "kernel",
)
CATEGORY_LABELS = {
    "servers": "NETWORK SERVERS",
    "clients": "NETWORK CLIENTS",
    "writers": "DISK WRITERS",
    "compute": "COMPUTE",
    "interactive": "INTERACTIVE",
    "daemons": "DAEMONS",
    "idle": "IDLE",
    "kernel": "KERNEL THREADS",
}
CATEGORY_SHORT = {
    "servers": "SERVERS",
    "clients": "CLIENTS",
    "writers": "WRITERS",
    "compute": "COMPUTE",
    "interactive": "SHELL",
    "daemons": "DAEMONS",
    "idle": "IDLE",
    "kernel": "KERNEL",
}
GROUP_NOVEL = "NEW & CHANGING"

CAPABILITY_NAMES = (
    "CAP_CHOWN",
    "CAP_DAC_OVERRIDE",
    "CAP_DAC_READ_SEARCH",
    "CAP_FOWNER",
    "CAP_FSETID",
    "CAP_KILL",
    "CAP_SETGID",
    "CAP_SETUID",
    "CAP_SETPCAP",
    "CAP_LINUX_IMMUTABLE",
    "CAP_NET_BIND_SERVICE",
    "CAP_NET_BROADCAST",
    "CAP_NET_ADMIN",
    "CAP_NET_RAW",
    "CAP_IPC_LOCK",
    "CAP_IPC_OWNER",
    "CAP_SYS_MODULE",
    "CAP_SYS_RAWIO",
    "CAP_SYS_CHROOT",
    "CAP_SYS_PTRACE",
    "CAP_SYS_PACCT",
    "CAP_SYS_ADMIN",
    "CAP_SYS_BOOT",
    "CAP_SYS_NICE",
    "CAP_SYS_RESOURCE",
    "CAP_SYS_TIME",
    "CAP_SYS_TTY_CONFIG",
    "CAP_MKNOD",
    "CAP_LEASE",
    "CAP_AUDIT_WRITE",
    "CAP_AUDIT_CONTROL",
    "CAP_SETFCAP",
    "CAP_MAC_OVERRIDE",
    "CAP_MAC_ADMIN",
    "CAP_SYSLOG",
    "CAP_WAKE_ALARM",
    "CAP_BLOCK_SUSPEND",
    "CAP_AUDIT_READ",
    "CAP_PERFMON",
    "CAP_BPF",
    "CAP_CHECKPOINT_RESTORE",
)

CAP_WEIGHTS = {
    "CAP_SYS_ADMIN": 30,
    "CAP_SYS_MODULE": 25,
    "CAP_SYS_PTRACE": 20,
    "CAP_NET_ADMIN": 20,
    "CAP_NET_RAW": 15,
    "CAP_DAC_READ_SEARCH": 15,
    "CAP_DAC_OVERRIDE": 15,
    "CAP_SYS_BOOT": 15,
    "CAP_BPF": 15,
    "CAP_MAC_ADMIN": 15,
    "CAP_AUDIT_CONTROL": 15,
    "CAP_SETUID": 10,
    "CAP_SETGID": 10,
    "CAP_CHOWN": 10,
    "CAP_PERFMON": 10,
    "CAP_SYS_RESOURCE": 10,
    "CAP_SYS_TIME": 10,
    "CAP_SYSLOG": 10,
    "CAP_SYS_CHROOT": 5,
    "CAP_KILL": 5,
}
DANGEROUS_CAPS = frozenset(CAP_WEIGHTS)

STATE_NAMES = {
    "01": "ESTAB",
    "02": "SYN-SENT",
    "03": "SYN-RECV",
    "04": "FIN-WAIT1",
    "05": "FIN-WAIT2",
    "06": "TIME-WAIT",
    "07": "CLOSE",
    "08": "CLOSE-WAIT",
    "09": "LAST-ACK",
    "0A": "LISTEN",
    "0B": "CLOSING",
    "0C": "NEW-SYN-RECV",
}

_USER_NAMES: dict[int, str] = {}


# ---------------------------------------------------------------------------
# XDG paths
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Paths:
    """Resolved XDG directories used by procwatch."""

    state: Path
    config: Path
    cache: Path
    runtime: Path

    @property
    def state_dir(self) -> Path:
        return self.state / "procwatch"

    @property
    def config_dir(self) -> Path:
        return self.config / "procwatch"

    @property
    def cache_dir(self) -> Path:
        return self.cache / "procwatch"

    @property
    def db(self) -> Path:
        return self.state_dir / "baseline.db"

    @property
    def config_file(self) -> Path:
        return self.config_dir / "config.toml"

    @property
    def log(self) -> Path:
        return self.state_dir / "procwatch.log"

    @property
    def cache_file(self) -> Path:
        return self.cache_dir / "last-snapshot.json"

    @property
    def lock(self) -> Path:
        return self.runtime / "procwatch.lock"

    def ensure(self) -> Paths:
        for directory in (
            self.state_dir,
            self.config_dir,
            self.cache_dir,
            self.runtime,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        return self


def _xdg_dir(env: Mapping[str, str], key: str, fallback: str) -> Path:
    value = env.get(key)
    if value:
        path = Path(value)
        if path.is_absolute():
            return path
    return Path(env.get("HOME") or Path.home()) / fallback


def xdg_paths(env: Mapping[str, str] | None = None) -> Paths:
    """Return procwatch's XDG paths, honoring XDG_* environment variables."""
    env = os.environ if env is None else env
    state = _xdg_dir(env, "XDG_STATE_HOME", ".local/state")
    runtime = env.get("XDG_RUNTIME_DIR")
    runtime_path = Path(runtime) if runtime and Path(runtime).is_absolute() else state
    return Paths(
        state=state,
        config=_xdg_dir(env, "XDG_CONFIG_HOME", ".config"),
        cache=_xdg_dir(env, "XDG_CACHE_HOME", ".cache"),
        runtime=runtime_path,
    )


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Config:
    """Thresholds and retention settings."""

    interval: float = 2.0
    rare_observations: int = 3
    dormant_days: float = 7.0
    write_rate: float = 1024**2
    read_rate: float = 4 * 1024**2
    cpu_percent: float = 25.0
    history_days: float = 14.0
    warm_identities: int = 50
    novel_group_score: int = 40
    event_min_score: int = 40
    event_dedupe_seconds: float = 3600.0
    behavior_min_observations: int = 5
    z_warn: float = 2.5
    z_high: float = 4.0
    suspicious_paths: tuple[str, ...] = ("/tmp/", "/var/tmp/", "/dev/shm/")

    @classmethod
    def load(cls, path: Path | str | None = None) -> Config:
        """Load TOML config, returning defaults when the file is absent."""
        if path is None:
            return cls()
        path = Path(path)
        if not path.exists():
            return cls()
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        values: dict[str, Any] = {}
        aliases = {
            "write_rate_mb": ("write_rate", 1024**2),
            "read_rate_mb": ("read_rate", 1024**2),
        }
        known = {f.name for f in dataclasses.fields(cls)}
        for key, value in data.items():
            if key in aliases:
                target, scale = aliases[key]
                values[target] = float(value) * scale
            elif key in known:
                values[key] = value
            else:
                LOG.warning("config: ignoring unknown key %r", key)
        if "suspicious_paths" in values:
            values["suspicious_paths"] = tuple(
                str(item) for item in values["suspicious_paths"]
            )
        return cls(**values)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def format_bytes(value: float) -> str:
    """Format a byte count with a binary unit suffix."""
    number = float(value)
    for unit in ("B", "K", "M", "G", "T"):
        if abs(number) < 1024 or unit == "T":
            if unit == "B":
                return f"{number:.0f}B"
            if abs(number) < 10:
                return f"{number:.1f}{unit}"
            return f"{number:.0f}{unit}"
        number /= 1024
    return f"{number:.0f}T"


def format_rate(value: float) -> str:
    """Format a per-second rate."""
    return f"{format_bytes(value)}/s"


def format_age(seconds: float) -> str:
    """Format an age as seconds, minutes, hours, or days."""
    seconds = max(0.0, seconds)
    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        return f"{int(seconds // 60)}m"
    if seconds < 86400:
        return f"{int(seconds // 3600)}h"
    return f"{int(seconds // 86400)}d"


def truncate(text: str, width: int) -> str:
    """Truncate text to width, using an ellipsis when it does not fit."""
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width == 1:
        return text[:1]
    return text[: width - 1] + "…"


def _user_name(uid: int) -> str:
    if uid not in _USER_NAMES:
        try:
            _USER_NAMES[uid] = pwd.getpwuid(uid).pw_name
        except KeyError:
            _USER_NAMES[uid] = str(uid)
    return _USER_NAMES[uid]


# ---------------------------------------------------------------------------
# /proc model
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Socket:
    """One socket from /proc/net/*."""

    proto: str
    inode: int
    local: str
    remote: str
    state: str
    uid: int
    listening: bool = False
    port: int | None = None


@dataclass(frozen=True, slots=True)
class NetBytes:
    """Cumulative TCP byte counters reported by ss."""

    sent: int = 0
    received: int = 0


@dataclass(frozen=True, slots=True)
class Process:
    """A single /proc/<pid> sample."""

    pid: int
    ppid: int = 0
    uid: int = 0
    euid: int = 0
    comm: str = ""
    cmdline: str = ""
    exe: str = ""
    exe_deleted: bool = False
    state: str = ""
    tty_nr: int = 0
    tty_fd: bool = False
    threads: int = 1
    rss_bytes: int = 0
    cpu_seconds: float = 0.0
    starttime: int = 0
    started_at: float = 0.0
    read_bytes: int = 0
    write_bytes: int = 0
    syscr: int = 0
    syscw: int = 0
    open_files: int = 0
    open_writes: int = 0
    sockets: tuple[Socket, ...] = ()
    caps: frozenset[str] = frozenset()
    seccomp: int = 0
    no_new_privs: bool = False
    cgroup: str = ""
    io_readable: bool = True
    fingerprint: str = ""

    @property
    def inet_sockets(self) -> tuple[Socket, ...]:
        return tuple(sock for sock in self.sockets if sock.proto != "unix")

    @property
    def listeners(self) -> tuple[Socket, ...]:
        return tuple(sock for sock in self.inet_sockets if sock.listening)

    @property
    def connections(self) -> tuple[Socket, ...]:
        return tuple(sock for sock in self.inet_sockets if not sock.listening)

    @property
    def unix_sockets(self) -> tuple[Socket, ...]:
        return tuple(sock for sock in self.sockets if sock.proto == "unix")

    @property
    def listen_ports(self) -> frozenset[int]:
        return frozenset(sock.port for sock in self.listeners if sock.port)

    @property
    def remote_endpoints(self) -> frozenset[str]:
        return frozenset(sock.remote for sock in self.connections if sock.remote)

    @property
    def tty(self) -> bool:
        return self.tty_nr != 0 or self.tty_fd


@dataclass(frozen=True, slots=True)
class SystemSnapshot:
    """All processes and network counters from one sample."""

    ts: float
    processes: tuple[Process, ...]
    net: Mapping[int, NetBytes] = field(default_factory=dict)
    ss_available: bool = False
    errors: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProcStat:
    comm: str
    state: str
    ppid: int
    tty_nr: int
    utime: int
    stime: int
    threads: int
    starttime: int


def parse_proc_stat(text: str) -> ProcStat:
    """Parse /proc/<pid>/stat, tolerating spaces and parens in comm."""
    open_paren = text.find("(")
    close_paren = text.rfind(")")
    if open_paren < 0 or close_paren < 0:
        raise ValueError("malformed proc stat")
    comm = text[open_paren + 1 : close_paren]
    fields = text[close_paren + 2 :].split()
    if len(fields) < 20:
        raise ValueError("short proc stat")
    return ProcStat(
        comm=comm,
        state=fields[0],
        ppid=int(fields[1]),
        tty_nr=int(fields[4]),
        utime=int(fields[11]),
        stime=int(fields[12]),
        threads=int(fields[17]),
        starttime=int(fields[19]),
    )


def decode_inet_addr(value: str, family: int) -> tuple[str, int]:
    """Decode an inet address from /proc/net/tcp{,6}."""
    if ":" in value:
        address_hex, port_hex = value.rsplit(":", 1)
    else:
        address_hex, port_hex = value, "0"
    port = int(port_hex, 16)
    if family == 4:
        raw = bytes.fromhex(address_hex)
        if len(raw) != 4:
            return value, port
        address = socketlib.inet_ntop(socketlib.AF_INET, raw[::-1])
    else:
        raw = bytes.fromhex(address_hex)
        if len(raw) != 16:
            return value, port
        packed = b"".join(raw[index : index + 4][::-1] for index in range(0, 16, 4))
        address = socketlib.inet_ntop(socketlib.AF_INET6, packed)
    return address, port


def format_endpoint(address: str, port: int) -> str:
    """Format an address:port pair for display."""
    if not port:
        return ""
    if address in ("0.0.0.0", "::"):
        return f":{port}"
    if ":" in address:
        return f"[{address}]:{port}"
    return f"{address}:{port}"


def parse_net_table(text: str, proto: str) -> dict[int, Socket]:
    """Parse /proc/net/{tcp,tcp6,udp,udp6}."""
    family = 6 if proto.endswith("6") else 4
    result: dict[int, Socket] = {}
    for line in text.splitlines():
        fields = line.split()
        if len(fields) < 10 or not fields[0].endswith(":"):
            continue
        try:
            local_address, local_port = decode_inet_addr(fields[1], family)
            remote_address, remote_port = decode_inet_addr(fields[2], family)
            inode = int(fields[9])
            uid = int(fields[7])
        except (ValueError, OSError):
            continue
        if inode == 0:
            continue
        state_code = fields[3]
        state = STATE_NAMES.get(state_code, state_code)
        listening = False
        if proto.startswith("tcp"):
            listening = state_code == "0A"
        elif proto.startswith("udp"):
            listening = remote_port == 0 and local_port != 0
            if listening and state_code == "07":
                state = "BOUND"
        result[inode] = Socket(
            proto=proto,
            inode=inode,
            local=format_endpoint(local_address, local_port),
            remote=format_endpoint(remote_address, remote_port),
            state=state,
            uid=uid,
            listening=listening,
            port=local_port,
        )
    return result


def parse_unix_table(text: str) -> dict[int, Socket]:
    """Parse /proc/net/unix."""
    result: dict[int, Socket] = {}
    for line in text.splitlines():
        fields = line.split(maxsplit=7)
        if len(fields) < 7 or not fields[0].endswith(":"):
            continue
        try:
            flags = int(fields[3], 16)
            inode = int(fields[6])
        except ValueError:
            continue
        if inode == 0:
            continue
        path = fields[7].strip() if len(fields) > 7 else ""
        listening = bool(flags & 0x10000)
        result[inode] = Socket(
            proto="unix",
            inode=inode,
            local=path or f"unix:{inode}",
            remote="",
            state="LISTEN" if listening else "CONN",
            uid=0,
            listening=listening,
        )
    return result


def parse_ss_tcp_info(text: str) -> dict[int, NetBytes]:
    """Sum bytes_sent/bytes_received from `ss -tinp` output per pid."""
    totals: dict[int, NetBytes] = {}
    current: set[int] = set()
    for line in text.splitlines():
        if not line.strip():
            continue
        if not line[0].isspace():
            current = {int(match) for match in re.findall(r"\bpid=(\d+)", line)}
        if not current:
            continue
        sent = re.search(r"\bbytes_sent:(\d+)", line)
        received = re.search(r"\bbytes_received:(\d+)", line)
        if not sent and not received:
            continue
        add_sent = int(sent.group(1)) if sent else 0
        add_received = int(received.group(1)) if received else 0
        for pid in current:
            old = totals.get(pid, NetBytes())
            totals[pid] = NetBytes(old.sent + add_sent, old.received + add_received)
    return totals


def query_ss(timeout: float = 3.0) -> tuple[str, bool]:
    """Return `ss -tinp` output and whether it succeeded."""
    if shutil.which("ss") is None:
        return "", False
    try:
        proc = subprocess.run(
            ["ss", "-t", "-i", "-n", "-p", "-H"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
        )
    except (OSError, subprocess.SubprocessError):
        LOG.debug("ss failed", exc_info=True)
        return "", False
    return proc.stdout, proc.returncode == 0


def capability_names(mask: int) -> frozenset[str]:
    """Decode a CapEff bitmask into capability names."""
    return frozenset(
        name for index, name in enumerate(CAPABILITY_NAMES) if mask & (1 << index)
    )


class Procfs:
    """Read /proc, optionally from a fake root for tests or demos."""

    def __init__(
        self,
        root: Path | str = Path("/proc"),
        *,
        use_ss: bool = True,
        max_fds: int = 4096,
        clock_ticks: int | None = None,
    ) -> None:
        self.root = Path(root)
        self.use_ss = use_ss
        self.max_fds = max_fds
        if clock_ticks is None:
            try:
                clock_ticks = os.sysconf("SC_CLK_TCK")
            except (ValueError, OSError):
                clock_ticks = 100
        self.clock_ticks = clock_ticks
        self.boot_time = self._read_boot_time()

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def _read_boot_time(self) -> float:
        for line in self._read_text(self.root / "stat").splitlines():
            if line.startswith("btime "):
                try:
                    return float(line.split()[1])
                except (IndexError, ValueError):
                    pass
        return 0.0

    def _read_net(self) -> dict[int, Socket]:
        sockets: dict[int, Socket] = {}
        for proto in ("tcp", "tcp6", "udp", "udp6"):
            text = self._read_text(self.root / "net" / proto)
            if text:
                sockets.update(parse_net_table(text, proto))
        text = self._read_text(self.root / "net" / "unix")
        if text:
            sockets.update(parse_unix_table(text))
        return sockets

    def snapshot(self, now: float | None = None) -> SystemSnapshot:
        """Take one system snapshot."""
        ts = time.time() if now is None else now
        net_sockets = self._read_net()
        errors: list[str] = []
        processes: list[Process] = []
        try:
            entries = sorted(
                (entry for entry in os.scandir(self.root) if entry.name.isdigit()),
                key=lambda entry: int(entry.name),
            )
        except OSError as exc:
            return SystemSnapshot(ts=ts, processes=(), errors=(str(exc),))
        for entry in entries:
            try:
                process = self._read_process(Path(entry.path), net_sockets, ts)
            except FileNotFoundError:
                errors.append(f"{entry.name}: vanished")
                continue
            except (OSError, ValueError) as exc:
                errors.append(f"{entry.name}: {exc}")
                continue
            if process is not None:
                processes.append(process)
        if self.use_ss:
            ss_text, ss_ok = query_ss()
        else:
            ss_text, ss_ok = "", False
        net = parse_ss_tcp_info(ss_text) if ss_ok else {}
        return SystemSnapshot(
            ts=ts,
            processes=tuple(processes),
            net=net,
            ss_available=ss_ok,
            errors=tuple(errors[:20]),
        )

    def _read_process(
        self, directory: Path, net_sockets: Mapping[int, Socket], now: float
    ) -> Process | None:
        stat_text = (directory / "stat").read_text(encoding="utf-8", errors="replace")
        parsed = parse_proc_stat(stat_text)
        status_text = self._read_text(directory / "status")
        uid, euid = self._parse_uid(status_text, directory)
        rss = 0
        threads = parsed.threads
        caps: frozenset[str] = frozenset()
        seccomp = 0
        no_new_privs = False
        for line in status_text.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            value = value.strip()
            if key == "VmRSS":
                try:
                    rss = int(value.split()[0]) * 1024
                except (IndexError, ValueError):
                    pass
            elif key == "Threads":
                try:
                    threads = int(value)
                except ValueError:
                    pass
            elif key == "CapEff":
                try:
                    caps = capability_names(int(value, 16))
                except ValueError:
                    pass
            elif key == "Seccomp":
                try:
                    seccomp = int(value)
                except ValueError:
                    pass
            elif key == "NoNewPrivs":
                no_new_privs = value == "1"

        cmdline_raw = b""
        try:
            cmdline_raw = (directory / "cmdline").read_bytes()
        except OSError:
            pass
        cmdline = (
            cmdline_raw.rstrip(b"\0")
            .replace(b"\0", b" ")
            .decode("utf-8", "replace")
            .replace("\n", " ")
            .strip()
        )[:8192]
        comm = parsed.comm.strip()
        exe, exe_deleted = self._read_exe(directory)
        cgroup = self._read_cgroup(directory)

        read_bytes = write_bytes = syscr = syscw = 0
        io_readable = True
        io_text = self._read_text(directory / "io")
        if io_text:
            for line in io_text.splitlines():
                key, _, value = line.partition(":")
                try:
                    number = int(value.strip())
                except ValueError:
                    continue
                if key == "read_bytes":
                    read_bytes = number
                elif key == "write_bytes":
                    write_bytes = number
                elif key == "syscr":
                    syscr = number
                elif key == "syscw":
                    syscw = number
        else:
            io_readable = False

        sockets, open_files, open_writes, tty_fd = self._read_fds(
            directory, net_sockets
        )
        fingerprint = process_fingerprint(exe, cmdline, comm, uid)
        started_at = (
            self.boot_time + parsed.starttime / self.clock_ticks
            if self.boot_time
            else 0.0
        )
        return Process(
            pid=int(directory.name),
            ppid=parsed.ppid,
            uid=uid,
            euid=euid,
            comm=comm,
            cmdline=cmdline,
            exe=exe,
            exe_deleted=exe_deleted,
            state=parsed.state,
            tty_nr=parsed.tty_nr,
            tty_fd=tty_fd,
            threads=threads,
            rss_bytes=rss,
            cpu_seconds=(parsed.utime + parsed.stime) / self.clock_ticks,
            starttime=parsed.starttime,
            started_at=started_at,
            read_bytes=read_bytes,
            write_bytes=write_bytes,
            syscr=syscr,
            syscw=syscw,
            open_files=open_files,
            open_writes=open_writes,
            sockets=sockets,
            caps=caps,
            seccomp=seccomp,
            no_new_privs=no_new_privs,
            cgroup=cgroup,
            io_readable=io_readable,
            fingerprint=fingerprint,
        )

    def _parse_uid(self, status_text: str, directory: Path) -> tuple[int, int]:
        for line in status_text.splitlines():
            if line.startswith("Uid:"):
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        return int(parts[1]), int(parts[2])
                    except ValueError:
                        break
        try:
            return directory.stat().st_uid, directory.stat().st_uid
        except OSError:
            return 0, 0

    def _read_exe(self, directory: Path) -> tuple[str, bool]:
        try:
            target = os.readlink(directory / "exe")
        except OSError:
            return "", False
        deleted = target.endswith(" (deleted)")
        if deleted:
            target = target[: -len(" (deleted)")]
        return target, deleted

    def _read_cgroup(self, directory: Path) -> str:
        text = self._read_text(directory / "cgroup")
        for line in text.splitlines():
            if line.startswith("0::"):
                return line[3:].strip()
        return text.strip()

    def _read_fds(
        self, directory: Path, net_sockets: Mapping[int, Socket]
    ) -> tuple[tuple[Socket, ...], int, int, bool]:
        sockets: dict[int, Socket] = {}
        open_files = 0
        open_writes = 0
        tty_fd = False
        fd_dir = directory / "fd"
        try:
            entries = list(os.scandir(fd_dir))
        except OSError:
            return (), 0, 0, False
        for index, entry in enumerate(entries):
            if index >= self.max_fds:
                LOG.debug("pid %s: fd scan capped at %s", directory.name, self.max_fds)
                break
            try:
                target = os.readlink(entry.path)
            except OSError:
                continue
            if target.startswith("socket:["):
                try:
                    inode = int(target[8:-1])
                except ValueError:
                    continue
                sock = net_sockets.get(inode)
                if sock is not None:
                    sockets[inode] = sock
                continue
            if target.startswith("/dev/pts/") or target in ("/dev/tty", "/dev/console"):
                tty_fd = True
            if not target.startswith("/") or target.startswith(
                ("/dev/", "/proc/", "/sys/")
            ):
                continue
            open_files += 1
            if self._fd_is_writable(directory, entry.name):
                open_writes += 1
        return tuple(sockets.values()), open_files, open_writes, tty_fd

    def _fd_is_writable(self, directory: Path, fd: str) -> bool:
        text = self._read_text(directory / "fdinfo" / fd)
        for line in text.splitlines():
            if line.startswith("flags:"):
                try:
                    flags = int(line.split(":", 1)[1].strip(), 8)
                except ValueError:
                    return False
                return (flags & os.O_ACCMODE) in (os.O_WRONLY, os.O_RDWR) or bool(
                    flags & os.O_APPEND
                )
        return False


def process_fingerprint(exe: str, cmdline: str, comm: str, uid: int) -> str:
    """Stable identity for a command, independent of pid.

    Kernel threads have no exe or cmdline and their comm often contains
    per-instance suffixes such as ``kworker/13:1-mm_percpu_wq``. Fold those
    into one identity so worker churn does not look like new software.
    """
    if not exe and not cmdline:
        base = re.split(r"[/:+]", comm.strip("[]"), maxsplit=1)[0] or comm
        raw = f"kernel\x00{base}"
    else:
        raw = "\0".join((exe or comm, cmdline, str(uid)))
    return hashlib.sha1(raw.encode("utf-8", "replace")).hexdigest()[:20]


# ---------------------------------------------------------------------------
# Rates
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Rates:
    """Per-process deltas between two samples."""

    cpu_percent: float = 0.0
    read_rate: float = 0.0
    write_rate: float = 0.0
    tx_rate: float = 0.0
    rx_rate: float = 0.0
    elapsed: float = 0.0


class RateTracker:
    """Compute per-process rates from consecutive snapshots."""

    def __init__(self) -> None:
        self.previous_ts: float | None = None
        self.previous: dict[int, tuple[int, float, int, int]] = {}
        self.previous_net: dict[int, NetBytes] = {}

    def update(self, snapshot: SystemSnapshot) -> dict[int, Rates]:
        rates: dict[int, Rates] = {}
        elapsed = 0.0
        if self.previous_ts is not None:
            elapsed = max(0.0, snapshot.ts - self.previous_ts)
        for process in snapshot.processes:
            rate = Rates(elapsed=elapsed)
            old = self.previous.get(process.pid)
            if old is not None and old[0] == process.starttime and elapsed > 0:
                _, old_cpu, old_read, old_write = old
                rate = Rates(
                    cpu_percent=max(
                        0.0, (process.cpu_seconds - old_cpu) / elapsed * 100.0
                    ),
                    read_rate=max(0.0, (process.read_bytes - old_read) / elapsed),
                    write_rate=max(0.0, (process.write_bytes - old_write) / elapsed),
                    elapsed=elapsed,
                )
            net_old = self.previous_net.get(process.pid, NetBytes())
            net_now = snapshot.net.get(process.pid, NetBytes())
            if elapsed > 0:
                rate = dataclasses.replace(
                    rate,
                    tx_rate=max(0.0, (net_now.sent - net_old.sent) / elapsed),
                    rx_rate=max(0.0, (net_now.received - net_old.received) / elapsed),
                )
            rates[process.pid] = rate
            self.previous[process.pid] = (
                process.starttime,
                process.cpu_seconds,
                process.read_bytes,
                process.write_bytes,
            )
        self.previous_ts = snapshot.ts
        self.previous_net = dict(snapshot.net)
        return rates


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


def permission_score(process: Process) -> int:
    """Weighted privilege/access score used by the PERM sort."""
    score = 20 if process.euid == 0 else 0
    score += sum(CAP_WEIGHTS.get(cap, 2) for cap in process.caps)
    score = min(score, 100)
    score += min(20, process.open_writes)
    score += min(5, process.open_files // 10)
    return score


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------


SCHEMA = """
CREATE TABLE IF NOT EXISTS identities (
    fingerprint TEXT PRIMARY KEY,
    exe TEXT NOT NULL DEFAULT '',
    cmdline TEXT NOT NULL DEFAULT '',
    comm TEXT NOT NULL DEFAULT '',
    uid INTEGER NOT NULL DEFAULT 0,
    first_seen REAL NOT NULL,
    last_seen REAL NOT NULL,
    observations INTEGER NOT NULL DEFAULT 0,
    last_pid INTEGER NOT NULL DEFAULT 0,
    sockets_mean REAL NOT NULL DEFAULT 0,
    sockets_m2 REAL NOT NULL DEFAULT 0,
    write_mean REAL NOT NULL DEFAULT 0,
    write_m2 REAL NOT NULL DEFAULT 0,
    cpu_mean REAL NOT NULL DEFAULT 0,
    cpu_m2 REAL NOT NULL DEFAULT 0,
    ports TEXT NOT NULL DEFAULT '',
    caps TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    fingerprint TEXT NOT NULL,
    pid INTEGER NOT NULL,
    comm TEXT NOT NULL DEFAULT '',
    level TEXT NOT NULL,
    reasons TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS events_ts ON events(ts DESC);
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


@dataclass(frozen=True, slots=True)
class Profile:
    """Aggregated baseline for one fingerprint."""

    fingerprint: str = ""
    exe: str = ""
    cmdline: str = ""
    comm: str = ""
    uid: int = 0
    first_seen: float = 0.0
    last_seen: float = 0.0
    observations: int = 0
    last_pid: int = 0
    sockets_mean: float = 0.0
    sockets_m2: float = 0.0
    write_mean: float = 0.0
    write_m2: float = 0.0
    cpu_mean: float = 0.0
    cpu_m2: float = 0.0
    ports: frozenset[int] = frozenset()
    caps: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class Event:
    """One recorded anomaly."""

    id: int = 0
    ts: float = 0.0
    fingerprint: str = ""
    pid: int = 0
    comm: str = ""
    level: str = ""
    reasons: str = ""


class Baseline:
    """SQLite-backed process baseline and event log."""

    def __init__(self, path: Path | str, config: Config) -> None:
        self.path = Path(path)
        self.config = config
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, timeout=5.0)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.executescript(SCHEMA)
        self.conn.execute(
            "INSERT OR IGNORE INTO meta(key, value) VALUES('created_at', ?)",
            (str(time.time()),),
        )
        self.conn.commit()
        self.prune_events()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    def prune_events(self) -> None:
        cutoff = time.time() - self.config.history_days * 86400
        with self.conn:
            self.conn.execute("DELETE FROM events WHERE ts < ?", (cutoff,))

    def profiles(self) -> dict[str, Profile]:
        """Load all baseline profiles."""
        rows = self.conn.execute("SELECT * FROM identities").fetchall()
        result: dict[str, Profile] = {}
        for row in rows:
            result[row["fingerprint"]] = Profile(
                fingerprint=row["fingerprint"],
                exe=row["exe"],
                cmdline=row["cmdline"],
                comm=row["comm"],
                uid=row["uid"],
                first_seen=row["first_seen"],
                last_seen=row["last_seen"],
                observations=row["observations"],
                last_pid=row["last_pid"],
                sockets_mean=row["sockets_mean"],
                sockets_m2=row["sockets_m2"],
                write_mean=row["write_mean"],
                write_m2=row["write_m2"],
                cpu_mean=row["cpu_mean"],
                cpu_m2=row["cpu_m2"],
                ports=frozenset(
                    int(item) for item in str(row["ports"]).split(",") if item
                ),
                caps=frozenset(item for item in str(row["caps"]).split(",") if item),
            )
        return result

    def identity_count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) AS count FROM identities").fetchone()
        return int(row["count"])

    def record(
        self,
        processes: Sequence[Process],
        rates: Mapping[int, Rates],
        now: float,
        profiles: Mapping[str, Profile] | None = None,
    ) -> int:
        """Update baseline aggregates. Returns the number of new identities."""
        current = dict(profiles) if profiles is not None else self.profiles()
        new_identities = 0
        rows: list[tuple[Any, ...]] = []
        for process in processes:
            rate = rates.get(process.pid, Rates())
            profile = current.get(process.fingerprint)
            sockets = float(len(process.inet_sockets))
            if profile is None:
                new_identities += 1
                first_seen = now
                observations = 1
                sockets_mean, sockets_m2 = sockets, 0.0
                write_mean, write_m2 = rate.write_rate, 0.0
                cpu_mean, cpu_m2 = rate.cpu_percent, 0.0
                ports = process.listen_ports
                caps = process.caps
            else:
                first_seen = profile.first_seen
                observations = profile.observations
                sockets_mean, sockets_m2, observations = _welford(
                    profile.sockets_mean, profile.sockets_m2, observations, sockets
                )
                write_mean, write_m2, _ = _welford(
                    profile.write_mean,
                    profile.write_m2,
                    profile.observations,
                    rate.write_rate,
                )
                cpu_mean, cpu_m2, _ = _welford(
                    profile.cpu_mean,
                    profile.cpu_m2,
                    profile.observations,
                    rate.cpu_percent,
                )
                ports = profile.ports | process.listen_ports
                caps = profile.caps | process.caps
            current[process.fingerprint] = Profile(
                fingerprint=process.fingerprint,
                exe=process.exe,
                cmdline=process.cmdline,
                comm=process.comm,
                uid=process.uid,
                first_seen=first_seen,
                last_seen=now,
                observations=observations,
                last_pid=process.pid,
                sockets_mean=sockets_mean,
                sockets_m2=sockets_m2,
                write_mean=write_mean,
                write_m2=write_m2,
                cpu_mean=cpu_mean,
                cpu_m2=cpu_m2,
                ports=ports,
                caps=caps,
            )
            rows.append(
                (
                    process.fingerprint,
                    process.exe,
                    process.cmdline,
                    process.comm,
                    process.uid,
                    first_seen,
                    now,
                    observations,
                    process.pid,
                    sockets_mean,
                    sockets_m2,
                    write_mean,
                    write_m2,
                    cpu_mean,
                    cpu_m2,
                    ",".join(str(port) for port in sorted(ports)),
                    ",".join(sorted(caps)),
                )
            )
        if rows:
            with self.conn:
                self.conn.executemany(
                    """
                    INSERT INTO identities (
                        fingerprint, exe, cmdline, comm, uid, first_seen, last_seen,
                        observations, last_pid, sockets_mean, sockets_m2, write_mean,
                        write_m2, cpu_mean, cpu_m2, ports, caps
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(fingerprint) DO UPDATE SET
                        exe=excluded.exe,
                        cmdline=excluded.cmdline,
                        comm=excluded.comm,
                        uid=excluded.uid,
                        last_seen=excluded.last_seen,
                        observations=excluded.observations,
                        last_pid=excluded.last_pid,
                        sockets_mean=excluded.sockets_mean,
                        sockets_m2=excluded.sockets_m2,
                        write_mean=excluded.write_mean,
                        write_m2=excluded.write_m2,
                        cpu_mean=excluded.cpu_mean,
                        cpu_m2=excluded.cpu_m2,
                        ports=excluded.ports,
                        caps=excluded.caps
                    """,
                    rows,
                )
        return new_identities

    def record_event(
        self,
        ts: float,
        fingerprint: str,
        pid: int,
        comm: str,
        level: str,
        reasons: str,
        dedupe_seconds: float = 3600.0,
    ) -> bool:
        """Record an event unless the same fingerprint/level fired recently."""
        existing = self.conn.execute(
            "SELECT 1 FROM events WHERE fingerprint=? AND level=? AND ts>=? LIMIT 1",
            (fingerprint, level, ts - dedupe_seconds),
        ).fetchone()
        if existing:
            return False
        with self.conn:
            self.conn.execute(
                "INSERT INTO events(ts, fingerprint, pid, comm, level, reasons) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ts, fingerprint, pid, comm, level, reasons),
            )
        return True

    def recent_events(self, limit: int = 200) -> list[Event]:
        rows = self.conn.execute(
            "SELECT * FROM events ORDER BY ts DESC, id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [
            Event(
                id=row["id"],
                ts=row["ts"],
                fingerprint=row["fingerprint"],
                pid=row["pid"],
                comm=row["comm"],
                level=row["level"],
                reasons=row["reasons"],
            )
            for row in rows
        ]

    def stats(self) -> dict[str, Any]:
        row = self.conn.execute(
            "SELECT COUNT(*) AS identities, "
            "COALESCE(SUM(observations), 0) AS observations, "
            "COALESCE(MIN(first_seen), 0) AS first_seen, "
            "COALESCE(MAX(last_seen), 0) AS last_seen "
            "FROM identities"
        ).fetchone()
        events = self.conn.execute("SELECT COUNT(*) AS count FROM events").fetchone()
        size = 0
        for candidate in self.path.parent.glob(f"{self.path.name}*"):
            try:
                size += candidate.stat().st_size
            except OSError:
                pass
        return {
            "identities": int(row["identities"]),
            "observations": int(row["observations"]),
            "first_seen": float(row["first_seen"]),
            "last_seen": float(row["last_seen"]),
            "events": int(events["count"]),
            "size": size,
        }

    def reset(self) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM identities")
            self.conn.execute("DELETE FROM events")
            self.conn.execute(
                "INSERT INTO meta(key, value) VALUES('created_at', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(time.time()),),
            )
        self.conn.execute("VACUUM")


def _welford(
    mean: float, m2: float, count: int, value: float
) -> tuple[float, float, int]:
    count += 1
    delta = value - mean
    mean += delta / count
    m2 += delta * (value - mean)
    return mean, m2, count


def _zscore(x: float, mean: float, m2: float, count: int, floor: float) -> float:
    if count < 2 or x <= mean:
        return 0.0
    variance = m2 / (count - 1)
    scale = max(variance**0.5 if variance > 0 else 0.0, floor, abs(mean) * 0.1)
    return (x - mean) / scale


# ---------------------------------------------------------------------------
# Novelty
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Novelty:
    """Why a process is interesting right now."""

    score: int
    level: str
    reasons: tuple[str, ...]


def _suspicious_path(process: Process, config: Config) -> str:
    haystack = process.exe or process.cmdline
    for prefix in config.suspicious_paths:
        if haystack.startswith(prefix):
            return prefix
    return ""


def assess_novelty(
    process: Process,
    profile: Profile | None,
    rates: Rates,
    now: float,
    config: Config,
) -> Novelty:
    """Compare a process against its baseline and score the difference."""
    reasons: list[str] = []
    score = 0
    level = "KNOWN"

    def add(points: int, reason: str) -> None:
        nonlocal score
        score += points
        reasons.append(reason)

    if profile is None:
        level = "NEW"
        add(60, "first seen in baseline")
        if process.euid == 0:
            add(10, "runs as root")
        if process.exe_deleted:
            add(20, "executable deleted")
        suspicious = _suspicious_path(process, config)
        if suspicious:
            add(15, f"runs from {suspicious}")
        if process.listeners:
            ports = ", ".join(f":{port}" for port in sorted(process.listen_ports))
            add(10, f"listens on {ports}")
        new_caps = process.caps & DANGEROUS_CAPS
        if new_caps and process.euid != 0:
            add(10, "capabilities: " + ", ".join(sorted(new_caps)))
    else:
        if profile.observations >= config.behavior_min_observations:
            metrics = (
                (
                    "connections",
                    float(len(process.inet_sockets)),
                    profile.sockets_mean,
                    profile.sockets_m2,
                    1.0,
                    lambda v: f"{v:.0f}",
                ),
                (
                    "disk write",
                    rates.write_rate,
                    profile.write_mean,
                    profile.write_m2,
                    64 * 1024.0,
                    format_rate,
                ),
                (
                    "cpu",
                    rates.cpu_percent,
                    profile.cpu_mean,
                    profile.cpu_m2,
                    2.0,
                    lambda v: f"{v:.0f}%",
                ),
            )
            for label, value, mean, m2, floor, formatter in metrics:
                zscore = _zscore(value, mean, m2, profile.observations, floor)
                if zscore >= config.z_high:
                    add(30, f"{label} {formatter(value)} vs baseline {formatter(mean)}")
                elif zscore >= config.z_warn:
                    add(15, f"{label} {formatter(value)} vs baseline {formatter(mean)}")
        new_caps = (process.caps - profile.caps) & DANGEROUS_CAPS
        if new_caps:
            add(20, "new capabilities: " + ", ".join(sorted(new_caps)))
        new_ports = process.listen_ports - profile.ports
        if new_ports:
            add(
                25,
                "new listener " + ", ".join(f":{port}" for port in sorted(new_ports)),
            )
        if process.exe_deleted:
            add(15, "executable deleted")
        suspicious = _suspicious_path(process, config)
        if suspicious:
            add(10, f"runs from {suspicious}")
        if reasons:
            level = "CHANGED"
        elif profile.observations < config.rare_observations:
            level = "RARE"
            add(30, f"seen only {profile.observations} time(s)")
        elif now - profile.last_seen >= config.dormant_days * 86400:
            level = "RETURNING"
            add(30, f"not seen for {format_age(now - profile.last_seen)}")

    return Novelty(min(100, score), level, tuple(reasons))


def categorize(process: Process, rates: Rates, config: Config) -> str:
    """Assign the process to the activity group it most strongly exhibits."""
    if not process.exe and not process.cmdline:
        return "kernel"
    if process.listeners:
        return "servers"
    if process.connections:
        return "clients"
    if rates.write_rate >= config.write_rate:
        return "writers"
    if rates.cpu_percent >= config.cpu_percent:
        return "compute"
    if process.tty:
        return "interactive"
    if process.ppid == 1:
        return "daemons"
    return "idle"


def activity_tags(process: Process, rates: Rates, config: Config) -> tuple[str, ...]:
    """Short activity tags used in the table."""
    tags: list[str] = []
    if process.listeners:
        tags.append("LS")
    if process.connections:
        tags.append("NET")
    if rates.write_rate >= config.write_rate:
        tags.append("WR")
    if rates.read_rate >= config.read_rate:
        tags.append("RD")
    if rates.cpu_percent >= config.cpu_percent:
        tags.append("CPU")
    if process.tty:
        tags.append("TTY")
    return tuple(tags)


# ---------------------------------------------------------------------------
# Rows, sorting, grouping
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ViewRow:
    """A process plus its current metrics, ready for display."""

    process: Process
    rates: Rates
    novelty: Novelty
    category: str
    tags: tuple[str, ...]
    user: str
    perm: int
    conn_count: int
    listen_count: int
    remote_count: int
    write_rate: float
    tx_rate: float
    rx_rate: float
    read_rate: float
    cpu_percent: float
    rss: int
    first_seen: float = 0.0
    observations: int = 0

    @property
    def key(self) -> str:
        return f"{self.process.pid}:{self.process.starttime}"

    @property
    def display_command(self) -> str:
        return self.process.cmdline or f"[{self.process.comm}]"


def build_rows(
    processes: Sequence[Process],
    rates: Mapping[int, Rates],
    novelty: Mapping[int, Novelty],
    config: Config,
    profiles: Mapping[str, Profile] | None = None,
) -> list[ViewRow]:
    """Combine process samples, rates, and novelty into display rows."""
    profiles = profiles or {}
    rows: list[ViewRow] = []
    for process in processes:
        rate = rates.get(process.pid, Rates())
        assessment = novelty.get(process.pid, Novelty(0, "KNOWN", ()))
        profile = profiles.get(process.fingerprint)
        rows.append(
            ViewRow(
                process=process,
                rates=rate,
                novelty=assessment,
                category=categorize(process, rate, config),
                tags=activity_tags(process, rate, config),
                user=_user_name(process.uid),
                perm=permission_score(process),
                conn_count=len(process.inet_sockets),
                listen_count=len(process.listeners),
                remote_count=len(process.remote_endpoints),
                write_rate=rate.write_rate,
                tx_rate=rate.tx_rate,
                rx_rate=rate.rx_rate,
                read_rate=rate.read_rate,
                cpu_percent=rate.cpu_percent,
                rss=process.rss_bytes,
                first_seen=profile.first_seen if profile else 0.0,
                observations=profile.observations if profile else 0,
            )
        )
    return rows


def default_reverse(key: str) -> bool:
    """Most columns sort largest-first; names and pids sort ascending."""
    return key not in ("name", "pid")


def sort_rows(
    rows: Sequence[ViewRow], key: str, reverse: bool | None = None
) -> list[ViewRow]:
    """Sort rows by a named metric."""
    if reverse is None:
        reverse = default_reverse(key)
    key_functions = {
        "connections": lambda row: (row.conn_count, row.remote_count, row.listen_count),
        "perm": lambda row: row.perm,
        "write": lambda row: row.write_rate,
        "tx": lambda row: row.tx_rate,
        "cpu": lambda row: row.cpu_percent,
        "mem": lambda row: row.rss,
        "novelty": lambda row: row.novelty.score,
        "age": lambda row: row.process.started_at,
        "name": lambda row: row.process.comm.lower(),
        "pid": lambda row: row.process.pid,
    }
    key_function = key_functions.get(key, key_functions["novelty"])
    return sorted(
        rows,
        key=lambda row: (key_function(row), row.process.pid),
        reverse=reverse,
    )


def filter_rows(rows: Sequence[ViewRow], text: str) -> list[ViewRow]:
    """Filter rows on pid, name, command, user, category, level, or tag."""
    needle = text.strip().lower()
    if not needle:
        return list(rows)
    result: list[ViewRow] = []
    for row in rows:
        haystack = " ".join(
            (
                str(row.process.pid),
                str(row.process.uid),
                row.process.comm,
                row.process.cmdline,
                row.process.exe,
                row.user,
                row.category,
                row.novelty.level,
                " ".join(row.tags),
                " ".join(sorted(row.process.caps)),
            )
        ).lower()
        if needle in haystack:
            result.append(row)
    return result


def risk_reasons(process: Process, config: Config) -> tuple[str, ...]:
    """Explain why a process appears in the risk view."""
    reasons: list[str] = []
    if process.euid == 0:
        reasons.append("root")
    caps = sorted(process.caps & DANGEROUS_CAPS)
    if caps:
        reasons.append("caps " + ",".join(caps))
    if process.exe_deleted:
        reasons.append("deleted executable")
    suspicious = _suspicious_path(process, config)
    if suspicious:
        reasons.append(f"runs from {suspicious}")
    return tuple(reasons)


def risk_rows(rows: Sequence[ViewRow], config: Config) -> list[ViewRow]:
    """Keep only processes with privilege or location risk markers."""
    return [row for row in rows if risk_reasons(row.process, config)]


def tree_order(rows: Sequence[ViewRow]) -> list[tuple[ViewRow, int]]:
    """Order rows parent-first, with a depth for indentation."""
    by_pid = {row.process.pid: row for row in rows}
    children: dict[int, list[ViewRow]] = {}
    roots: list[ViewRow] = []
    for row in rows:
        parent = row.process.ppid
        if parent in by_pid and parent != row.process.pid:
            children.setdefault(parent, []).append(row)
        else:
            roots.append(row)

    ordered: list[tuple[ViewRow, int]] = []
    visited: set[str] = set()

    def walk(row: ViewRow, depth: int) -> None:
        if row.key in visited:
            return
        visited.add(row.key)
        ordered.append((row, depth))
        for child in sorted(
            children.get(row.process.pid, []), key=lambda item: item.process.pid
        ):
            walk(child, depth + 1)

    for root in sorted(roots, key=lambda item: item.process.pid):
        walk(root, 0)
    for row in sorted(rows, key=lambda item: item.process.pid):
        walk(row, 0)
    return ordered


@dataclass(frozen=True, slots=True)
class CommandRow:
    """All processes sharing one command identity, aggregated."""

    fingerprint: str
    comm: str
    members: tuple[ViewRow, ...]
    users: tuple[str, ...]
    category: str
    novelty: Novelty
    count: int
    conn_count: int
    listen_count: int
    perm: int
    write_rate: float
    tx_rate: float
    rx_rate: float
    read_rate: float
    cpu_percent: float
    rss: int
    tags: tuple[str, ...]
    first_seen: float = 0.0
    observations: int = 0

    @property
    def key(self) -> str:
        return f"cmd:{self.fingerprint}"

    @property
    def display_command(self) -> str:
        return self.members[0].display_command

    @property
    def pids(self) -> tuple[int, ...]:
        return tuple(sorted(member.process.pid for member in self.members))


@dataclass(frozen=True, slots=True)
class CgroupRow:
    """All processes in one cgroup, aggregated."""

    path: str
    name: str
    members: tuple[ViewRow, ...]
    users: tuple[str, ...]
    comms: tuple[str, ...]
    novelty: Novelty
    count: int
    perm: int
    write_rate: float
    tx_rate: float
    rx_rate: float
    read_rate: float
    cpu_percent: float
    rss: int
    first_seen: float = 0.0

    @property
    def key(self) -> str:
        return f"cg:{self.path}"


@dataclass(frozen=True, slots=True)
class EndpointRow:
    """One inet socket belonging to a process."""

    socket: Socket
    row: ViewRow
    exposure: str

    @property
    def key(self) -> str:
        process = self.row.process
        return f"{process.pid}:{process.starttime}:{self.socket.inode}"

    @property
    def display_command(self) -> str:
        return self.row.display_command


def _best_novelty(members: Sequence[ViewRow]) -> Novelty:
    return max(members, key=lambda row: row.novelty.score).novelty


def _first_seen(members: Sequence[ViewRow]) -> float:
    values = [row.first_seen for row in members if row.first_seen]
    return min(values) if values else 0.0


def aggregate_commands(rows: Sequence[ViewRow]) -> list[CommandRow]:
    """Collapse processes into one row per command fingerprint."""
    grouped: dict[str, list[ViewRow]] = {}
    for row in rows:
        grouped.setdefault(row.process.fingerprint, []).append(row)
    commands: list[CommandRow] = []
    for fingerprint, members in grouped.items():
        best = max(members, key=lambda row: (row.novelty.score, row.cpu_percent))
        tags = tuple(dict.fromkeys(tag for member in members for tag in member.tags))
        commands.append(
            CommandRow(
                fingerprint=fingerprint,
                comm=best.process.comm,
                members=tuple(members),
                users=tuple(sorted({member.user for member in members})),
                category=best.category,
                novelty=_best_novelty(members),
                count=len(members),
                conn_count=sum(member.conn_count for member in members),
                listen_count=sum(member.listen_count for member in members),
                perm=max(member.perm for member in members),
                write_rate=sum(member.write_rate for member in members),
                tx_rate=sum(member.tx_rate for member in members),
                rx_rate=sum(member.rx_rate for member in members),
                read_rate=sum(member.read_rate for member in members),
                cpu_percent=sum(member.cpu_percent for member in members),
                rss=sum(member.rss for member in members),
                tags=tags,
                first_seen=_first_seen(members),
                observations=max(member.observations for member in members),
            )
        )
    return commands


def aggregate_cgroups(rows: Sequence[ViewRow]) -> list[CgroupRow]:
    """Collapse processes into one row per cgroup."""
    grouped: dict[str, list[ViewRow]] = {}
    for row in rows:
        grouped.setdefault(row.process.cgroup or "(none)", []).append(row)
    cgroups: list[CgroupRow] = []
    for path, members in grouped.items():
        name = path.rstrip("/").rsplit("/", 1)[-1] or path
        cgroups.append(
            CgroupRow(
                path=path,
                name=name,
                members=tuple(members),
                users=tuple(sorted({member.user for member in members})),
                comms=tuple(sorted({member.process.comm for member in members})),
                novelty=_best_novelty(members),
                count=len(members),
                perm=max(member.perm for member in members),
                write_rate=sum(member.write_rate for member in members),
                tx_rate=sum(member.tx_rate for member in members),
                rx_rate=sum(member.rx_rate for member in members),
                read_rate=sum(member.read_rate for member in members),
                cpu_percent=sum(member.cpu_percent for member in members),
                rss=sum(member.rss for member in members),
                first_seen=_first_seen(members),
            )
        )
    return cgroups


def _socket_exposure(sock: Socket) -> str:
    if not sock.listening:
        return "REMOTE"
    local = sock.local
    if local.startswith((":", "0.0.0.0:", "[::]:")):
        return "PUBLIC"
    if local.startswith(("127.", "[::1]")):
        return "LOCAL"
    return "BOUND"


def build_endpoint_rows(rows: Sequence[ViewRow]) -> list[EndpointRow]:
    """Flatten process sockets into endpoint rows."""
    endpoints: list[EndpointRow] = []
    for row in rows:
        for sock in row.process.inet_sockets:
            endpoints.append(
                EndpointRow(socket=sock, row=row, exposure=_socket_exposure(sock))
            )
    return endpoints


def sort_commands(
    rows: Sequence[CommandRow], key: str, reverse: bool | None = None
) -> list[CommandRow]:
    if reverse is None:
        reverse = default_reverse(key)
    key_functions = {
        "connections": lambda row: row.conn_count,
        "perm": lambda row: row.perm,
        "write": lambda row: row.write_rate,
        "tx": lambda row: row.tx_rate,
        "cpu": lambda row: row.cpu_percent,
        "mem": lambda row: row.rss,
        "novelty": lambda row: row.novelty.score,
        "age": lambda row: row.first_seen,
        "name": lambda row: row.comm.lower(),
        "pid": lambda row: row.pids[0] if row.pids else 0,
    }
    key_function = key_functions.get(key, key_functions["novelty"])
    return sorted(rows, key=key_function, reverse=reverse)


def sort_cgroups(
    rows: Sequence[CgroupRow], key: str, reverse: bool | None = None
) -> list[CgroupRow]:
    if reverse is None:
        reverse = default_reverse(key)
    key_functions = {
        "connections": lambda row: row.count,
        "perm": lambda row: row.perm,
        "write": lambda row: row.write_rate,
        "tx": lambda row: row.tx_rate,
        "cpu": lambda row: row.cpu_percent,
        "mem": lambda row: row.rss,
        "novelty": lambda row: row.novelty.score,
        "age": lambda row: row.first_seen,
        "name": lambda row: row.name.lower(),
        "pid": lambda row: row.name.lower(),
    }
    key_function = key_functions.get(key, key_functions["novelty"])
    return sorted(rows, key=key_function, reverse=reverse)


def sort_endpoints(
    rows: Sequence[EndpointRow], key: str, reverse: bool | None = None
) -> list[EndpointRow]:
    if reverse is None:
        reverse = default_reverse(key)
    exposure_score = {"PUBLIC": 3, "BOUND": 2, "LOCAL": 1, "REMOTE": 0}
    key_functions = {
        "connections": lambda row: (
            exposure_score.get(row.exposure, 0),
            row.socket.port or 0,
        ),
        "perm": lambda row: row.row.perm,
        "write": lambda row: row.row.write_rate,
        "tx": lambda row: row.row.tx_rate,
        "cpu": lambda row: row.row.cpu_percent,
        "mem": lambda row: row.row.rss,
        "novelty": lambda row: row.row.novelty.score,
        "age": lambda row: row.row.process.started_at,
        "name": lambda row: row.row.process.comm.lower(),
        "pid": lambda row: row.row.process.pid,
    }
    key_function = key_functions.get(key, key_functions["connections"])
    return sorted(
        rows,
        key=lambda row: (
            key_function(row),
            row.socket.port or 0,
            row.socket.inode,
        ),
        reverse=reverse,
    )


def _sort_group(rows: Sequence[ViewRow]) -> list[ViewRow]:
    return sorted(
        rows,
        key=lambda row: (
            -row.novelty.score,
            -row.conn_count,
            -row.write_rate,
            row.process.comm.lower(),
            row.process.pid,
        ),
    )


def _is_novel(row: ViewRow, threshold: int) -> bool:
    """New/changed/returning always float; rare floats only when notable."""
    if row.novelty.level in ("NEW", "CHANGED", "RETURNING"):
        return True
    return row.novelty.level == "RARE" and row.novelty.score >= threshold


def group_rows(
    rows: Sequence[ViewRow], threshold: int = 30
) -> list[tuple[str, list[ViewRow]]]:
    """Group rows for the triage view, with novel rows removed from groups."""
    novel = [row for row in rows if _is_novel(row, threshold)]
    novel_ids = {row.key for row in novel}
    groups: list[tuple[str, list[ViewRow]]] = []
    if novel:
        groups.append((GROUP_NOVEL, _sort_group(novel)))
    for category in CATEGORY_ORDER:
        subset = [
            row for row in rows if row.key not in novel_ids and row.category == category
        ]
        if subset:
            groups.append((CATEGORY_LABELS[category], _sort_group(subset)))
    return groups


# ---------------------------------------------------------------------------
# Dashboard state and plain-text renderer (also used by --snapshot)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Span:
    text: str
    style: str = ""


@dataclass(frozen=True, slots=True)
class RenderLine:
    spans: tuple[Span, ...] = ()
    row_index: int | None = None

    @property
    def text(self) -> str:
        return "".join(span.text for span in self.spans)


NOVELTY_STYLES = {
    "NEW": "new",
    "CHANGED": "changed",
    "RETURNING": "returning",
    "RARE": "rare",
    "KNOWN": "",
}


class Dashboard:
    """Headless dashboard state: sampling, sorting, filtering, rendering."""

    def __init__(
        self,
        procfs: Procfs,
        baseline: Baseline,
        config: Config,
        *,
        record: bool = True,
    ) -> None:
        self.procfs = procfs
        self.baseline = baseline
        self.config = config
        self.record = record
        self.tracker = RateTracker()
        self.rows: list[ViewRow] = []
        self.events: list[Event] = []
        self.snapshot: SystemSnapshot | None = None
        self.rates: dict[int, Rates] = {}
        self.novelty: dict[int, Novelty] = {}
        self.profiles: dict[str, Profile] = {}
        self.snapshot_ts = 0.0
        self.identity_count = 0
        self.warming = True
        self.view = "main"
        self.sort_key = "connections"
        self.sort_reverse = True
        self.filter_text = ""
        self.novelty_filter = ""
        self.tree_mode = False
        self.tree_depths: dict[str, int] = {}
        self.selected = 0
        self.scroll = 0
        self.page_size = 10
        self.input_mode = False
        self.filter_buffer = ""
        self.last_error = ""

    def poll(self, now: float | None = None) -> None:
        """Take a sample, compute novelty, and update the baseline."""
        ts = time.time() if now is None else now
        try:
            snapshot = self.procfs.snapshot(now=ts)
        except OSError as exc:
            self.last_error = str(exc)
            LOG.error("snapshot failed: %s", exc)
            return
        rates = self.tracker.update(snapshot)
        profiles = self.baseline.profiles()
        identities_before = len(profiles)
        self.identity_count = identities_before
        self.warming = identities_before < self.config.warm_identities
        novelty = {
            process.pid: assess_novelty(
                process,
                profiles.get(process.fingerprint),
                rates.get(process.pid, Rates()),
                ts,
                self.config,
            )
            for process in snapshot.processes
        }
        rows = build_rows(snapshot.processes, rates, novelty, self.config, profiles)
        if self.record:
            if identities_before >= self.config.warm_identities:
                for row in rows:
                    if row.novelty.score >= self.config.event_min_score:
                        self.baseline.record_event(
                            ts,
                            row.process.fingerprint,
                            row.process.pid,
                            row.process.comm,
                            row.novelty.level,
                            "; ".join(row.novelty.reasons),
                            self.config.event_dedupe_seconds,
                        )
            self.baseline.record(snapshot.processes, rates, ts, profiles)
            self.identity_count = self.baseline.identity_count()
            self.warming = self.identity_count < self.config.warm_identities
        self.snapshot = snapshot
        self.snapshot_ts = ts
        self.rates = rates
        self.novelty = novelty
        self.profiles = profiles
        self.rows = rows
        self.events = self.baseline.recent_events(200)
        self.last_error = ""
        self._clamp_selection()

    # -- views ---------------------------------------------------------
    def set_view(self, view: str) -> None:
        if view not in VIEWS:
            raise ValueError(f"unknown view: {view}")
        if view != self.view:
            self.view = view
            self.selected = 0
            self.scroll = 0

    def set_sort(self, key: str, reverse: bool | None = None) -> None:
        if key not in SORT_KEYS:
            raise ValueError(f"unknown sort key: {key}")
        self.sort_key = key
        self.sort_reverse = default_reverse(key) if reverse is None else reverse
        self.selected = 0
        self.scroll = 0

    def sort_by(self, key: str) -> None:
        self.set_sort(key)

    def cycle_sort(self, direction: int = 1) -> None:
        index = SORT_KEYS.index(self.sort_key)
        self.set_sort(SORT_KEYS[(index + direction) % len(SORT_KEYS)])

    def toggle_reverse(self) -> None:
        self.sort_reverse = not self.sort_reverse

    def set_filter(self, text: str) -> None:
        self.filter_text = text.strip()
        self.selected = 0
        self.scroll = 0

    def begin_filter(self) -> None:
        self.input_mode = True
        self.filter_buffer = self.filter_text

    def handle_filter_key(self, key: int) -> None:
        if not self.input_mode:
            return
        if key in (10, 13):
            self.set_filter(self.filter_buffer)
            self.input_mode = False
        elif key == 27:
            self.input_mode = False
        elif key in (8, 127, 263):
            self.filter_buffer = self.filter_buffer[:-1]
        elif 32 <= key < 127:
            self.filter_buffer += chr(key)

    def toggle_tree(self) -> None:
        self.tree_mode = not self.tree_mode
        self.selected = 0
        self.scroll = 0

    def cycle_novelty_filter(self, direction: int = 1) -> None:
        index = NOVELTY_FILTERS.index(self.novelty_filter)
        self.novelty_filter = NOVELTY_FILTERS[
            (index + direction) % len(NOVELTY_FILTERS)
        ]
        self.selected = 0
        self.scroll = 0

    def filtered_rows(self) -> list[ViewRow]:
        rows = filter_rows(self.rows, self.filter_text)
        if self.novelty_filter:
            rows = [row for row in rows if row.novelty.level == self.novelty_filter]
        return rows

    def grouped_rows(self) -> list[tuple[str, list[ViewRow]]]:
        return group_rows(self.filtered_rows(), self.config.novel_group_score)

    def visible_items(self) -> list[Any]:
        """Rows for the active view, in display order."""
        self.tree_depths = {}
        if self.view == "main":
            return [row for _, group in self.grouped_rows() for row in group]
        if self.view == "all":
            filtered = self.filtered_rows()
            if self.tree_mode:
                ordered = tree_order(filtered)
                self.tree_depths = {row.key: depth for row, depth in ordered}
                return [row for row, _ in ordered]
            return sort_rows(filtered, self.sort_key, self.sort_reverse)
        if self.view == "risk":
            return sort_rows(
                risk_rows(self.filtered_rows(), self.config),
                self.sort_key,
                self.sort_reverse,
            )
        if self.view == "commands":
            return sort_commands(
                aggregate_commands(self.filtered_rows()),
                self.sort_key,
                self.sort_reverse,
            )
        if self.view == "network":
            return sort_endpoints(
                build_endpoint_rows(self.filtered_rows()),
                self.sort_key,
                self.sort_reverse,
            )
        if self.view == "cgroups":
            return sort_cgroups(
                aggregate_cgroups(self.filtered_rows()),
                self.sort_key,
                self.sort_reverse,
            )
        return []

    def visible_rows(self) -> list[ViewRow]:
        items = self.visible_items()
        return [item for item in items if isinstance(item, ViewRow)]

    def selected_item(self) -> Any | None:
        items = self.visible_items()
        if not items:
            return None
        return items[min(max(0, self.selected), len(items) - 1)]

    def selected_row(self) -> ViewRow | None:
        item = self.selected_item()
        return item if isinstance(item, ViewRow) else None

    def move_selection(self, delta: int) -> None:
        items = self.visible_items()
        if not items:
            return
        self.selected = min(max(0, self.selected + delta), len(items) - 1)

    def _clamp_selection(self) -> None:
        items = self.visible_items()
        if not items:
            self.selected = 0
            self.scroll = 0
            return
        self.selected = min(max(0, self.selected), len(items) - 1)

    def display_command(self, row: ViewRow) -> str:
        """Command text with tree indentation when tree mode is active."""
        depth = self.tree_depths.get(row.key, 0)
        if self.view == "all" and self.tree_mode and depth:
            return "  " * depth + row.display_command
        return row.display_command

    def totals(self) -> dict[str, Any]:
        levels = [row.novelty.level for row in self.rows]
        return {
            "processes": len(self.rows),
            "new": levels.count("NEW"),
            "changed": levels.count("CHANGED"),
            "rare": levels.count("RARE"),
            "returning": levels.count("RETURNING"),
            "sockets": sum(
                row.conn_count + len(row.process.unix_sockets) for row in self.rows
            ),
            "connections": sum(row.conn_count for row in self.rows),
            "write_rate": sum(row.write_rate for row in self.rows),
            "tx_rate": sum(row.tx_rate for row in self.rows),
            "identities": self.identity_count,
            "warming": self.warming,
            "net_available": bool(self.snapshot and self.snapshot.ss_available),
            "errors": len(self.snapshot.errors) if self.snapshot else 0,
        }

    # -- rendering -----------------------------------------------------
    def render(self, width: int, height: int) -> list[RenderLine]:
        """Render the dashboard as styled text lines."""
        width = max(20, width)
        height = max(8, height)
        detail_height = 5 if height < 32 else 6
        content_height = max(1, height - 4 - detail_height - 1)
        self.page_size = max(1, content_height - 2)

        totals = self.totals()
        lines: list[RenderLine] = [
            self._title_line(width),
            self._metrics_line(totals, width),
            self._tabs_line(width),
            RenderLine((Span("-" * width, "dim"),)),
        ]
        if self.view == "events":
            content = self._event_lines(width)
        else:
            content = self._content_lines(width)
            selectable = [
                index
                for index, line in enumerate(content)
                if line.row_index is not None
            ]
            if selectable:
                position = min(selectable, key=lambda item: abs(item - self.scroll))
                selected_line = next(
                    (
                        index
                        for index in selectable
                        if content[index].row_index == self.selected
                    ),
                    position,
                )
                if selected_line < self.scroll:
                    self.scroll = selected_line
                elif selected_line >= self.scroll + content_height:
                    self.scroll = selected_line - content_height + 1
                self.scroll = max(
                    0, min(self.scroll, max(0, len(content) - content_height))
                )
        visible = content[self.scroll : self.scroll + content_height]
        lines.extend(visible)
        lines.extend(
            RenderLine((Span("", ""),)) for _ in range(content_height - len(visible))
        )

        lines.append(RenderLine((Span("-" * width, "dim"),)))
        detail = self._detail_lines(width)
        visible_detail = detail[: detail_height - 1]
        lines.extend(visible_detail)
        lines.extend(
            RenderLine((Span("", ""),))
            for _ in range(detail_height - 1 - len(visible_detail))
        )
        lines.append(self._footer_line(width))
        return lines[:height]

    def _title_line(self, width: int) -> RenderLine:
        stamp = dt.datetime.fromtimestamp(self.snapshot_ts or time.time()).strftime(
            "%H:%M:%S"
        )
        left = [Span("procwatch", "title"), Span("  process baseline triage", "dim")]
        right = f"{stamp}  "
        used = sum(len(span.text) for span in left)
        gap = max(0, width - used - len(right))
        return RenderLine(tuple(left) + (Span(" " * gap + right, "dim"),))

    def _metrics_line(self, totals: Mapping[str, Any], width: int) -> RenderLine:
        net = (
            "tx " + format_rate(totals["tx_rate"])
            if totals["net_available"]
            else "tx n/a"
        )
        parts = [
            f"{totals['processes']} procs",
            f"{totals['new']} new",
            f"{totals['changed']} changed",
            f"{totals['rare']} rare",
            f"{totals['sockets']} sockets",
            f"write {format_rate(totals['write_rate'])}",
            net,
            f"baseline {totals['identities']}",
        ]
        if totals["warming"]:
            parts.append("warming")
        if self.filter_text:
            parts.append(f'filter "{self.filter_text}"')
        if self.novelty_filter:
            parts.append(f"novelty {self.novelty_filter}")
        if self.view == "all" and self.tree_mode:
            parts.append("tree")
        if self.view in ("all", "risk", "commands", "network", "cgroups"):
            parts.append(
                f"sort {SORT_LABELS[self.sort_key]} {'desc' if self.sort_reverse else 'asc'}"
            )
        text = " | ".join(parts)
        return RenderLine((Span(truncate(text, width), "dim"),))

    def _tabs_line(self, width: int) -> RenderLine:
        spans: list[Span] = []
        used = 0
        for key, number in (
            ("main", "1"),
            ("all", "2"),
            ("events", "3"),
            ("commands", "4"),
            ("network", "5"),
            ("cgroups", "6"),
            ("risk", "!"),
        ):
            active = self.view == key
            marker = ">" if active else " "
            chunk = f" {marker} {number} {VIEW_LABELS[key]} "
            if used + len(chunk) > width:
                break
            spans.append(Span(chunk, "tab-active" if active else "dim"))
            spans.append(Span(" ", ""))
            used += len(chunk) + 1
        return RenderLine(tuple(spans))

    def _novelty_badge(self, novelty: Novelty) -> str:
        return {
            "NEW": "NEW",
            "CHANGED": "CHG",
            "RETURNING": "RET",
            "RARE": "RARE",
            "KNOWN": "",
        }.get(novelty.level, novelty.level[:4])

    def _content_lines(self, width: int) -> list[RenderLine]:
        lines: list[RenderLine] = []
        if self.view == "main":
            lines.append(self._process_header(width))
            index = 0
            for group_name, rows in self.grouped_rows():
                lines.append(
                    RenderLine((Span(f"{group_name} ({len(rows)})", "header"),))
                )
                for row in rows:
                    lines.append(
                        self._process_line(row, width, index, include_extra=False)
                    )
                    index += 1
            if index == 0:
                lines.append(
                    RenderLine((Span("no processes match the filter", "dim"),))
                )
            return lines

        if self.view in ("all", "risk"):
            lines.append(self._process_header(width))
            items = self.visible_items()
            for index, row in enumerate(items):
                lines.append(self._process_line(row, width, index, include_extra=True))
            if not items:
                message = (
                    "no risky processes"
                    if self.view == "risk"
                    else "no processes match the filter"
                )
                lines.append(RenderLine((Span(message, "dim"),)))
            return lines

        if self.view == "commands":
            lines.append(self._command_header(width))
            commands = self.visible_items()
            for index, command in enumerate(commands):
                lines.append(self._command_line(command, width, index))
            if not commands:
                lines.append(RenderLine((Span("no commands match the filter", "dim"),)))
            return lines

        if self.view == "network":
            lines.append(self._endpoint_header(width))
            endpoints = self.visible_items()
            for index, endpoint in enumerate(endpoints):
                lines.append(self._endpoint_line(endpoint, width, index))
            if not endpoints:
                lines.append(RenderLine((Span("no sockets match the filter", "dim"),)))
            return lines

        if self.view == "cgroups":
            lines.append(self._cgroup_header(width))
            cgroups = self.visible_items()
            for index, cgroup in enumerate(cgroups):
                lines.append(self._cgroup_line(cgroup, width, index))
            if not cgroups:
                lines.append(RenderLine((Span("no cgroups match the filter", "dim"),)))
        return lines

    def _process_header(self, width: int) -> RenderLine:
        if self.view == "main":
            text = (
                f"{'PID':>7} {'NOV':<5} {'CONN':>5} {'PERM':>4} "
                f"{'WR/s':>8} {'CPU':>5} {'TAGS':<20} COMMAND"
            )
        else:
            arrow = "v" if self.sort_reverse else "^"
            labels = {}
            for key, label in SORT_LABELS.items():
                labels[key] = label + (arrow if key == self.sort_key else " ")
            text = (
                f"{'PID':>7} {'NOV':<5} {labels['connections']:>5} {labels['perm']:>4} "
                f"{labels['write']:>8} {labels['tx']:>8} {labels['cpu']:>5} "
                f"{labels['mem']:>6} {'TAGS':<20} {'USER':<8} COMMAND"
            )
        return RenderLine((Span(truncate(text, width), "header"),))

    def _proc_prefix(self, row: ViewRow, include_extra: bool) -> str:
        badge = self._novelty_badge(row.novelty)
        tags = ",".join(row.tags)
        if include_extra:
            return (
                f"{row.process.pid:>7} {badge:<5} {row.conn_count:>5} {row.perm:>4} "
                f"{format_rate(row.write_rate):>8} {format_rate(row.tx_rate):>8} "
                f"{row.cpu_percent:>4.0f}% {format_bytes(row.rss):>6} {tags:<20} "
                f"{row.user:<8} "
            )
        return (
            f"{row.process.pid:>7} {badge:<5} {row.conn_count:>5} {row.perm:>4} "
            f"{format_rate(row.write_rate):>8} {row.cpu_percent:>4.0f}% "
            f"{tags:<20} "
        )

    def _process_line(
        self, row: ViewRow, width: int, index: int, *, include_extra: bool
    ) -> RenderLine:
        selected = index == self.selected
        style = "selected" if selected else NOVELTY_STYLES.get(row.novelty.level, "")
        prefix = self._proc_prefix(row, include_extra)
        command = truncate(self.display_command(row), max(1, width - len(prefix)))
        spans = [Span(prefix, style)]
        spans.append(Span(command, "selected" if selected else ""))
        return RenderLine(tuple(spans), row_index=index)

    def _command_header(self, width: int) -> RenderLine:
        text = (
            f"{'COUNT':>5} {'NOV':<5} {'CONN':>5} {'PERM':>4} {'WR/s':>8} "
            f"{'TX/s':>8} {'CPU':>5} {'MEM':>6} {'USER':<8} COMMAND"
        )
        return RenderLine((Span(truncate(text, width), "header"),))

    def _command_line(self, row: CommandRow, width: int, index: int) -> RenderLine:
        selected = index == self.selected
        style = "selected" if selected else NOVELTY_STYLES.get(row.novelty.level, "")
        badge = self._novelty_badge(row.novelty)
        prefix = (
            f"{row.count:>5} {badge:<5} {row.conn_count:>5} {row.perm:>4} "
            f"{format_rate(row.write_rate):>8} {format_rate(row.tx_rate):>8} "
            f"{row.cpu_percent:>4.0f}% {format_bytes(row.rss):>6} "
            f"{truncate(','.join(row.users), 8):<8} "
        )
        command = truncate(row.display_command, max(1, width - len(prefix)))
        spans = [Span(prefix, style)]
        spans.append(Span(command, "selected" if selected else ""))
        return RenderLine(tuple(spans), row_index=index)

    def _endpoint_header(self, width: int) -> RenderLine:
        text = (
            f"{'PROTO':<5} {'LOCAL':<22} {'REMOTE':<22} {'STATE':<10} "
            f"{'EXPOSE':<7} {'PID':>7} {'USER':<8} {'NOV':<5} COMMAND"
        )
        return RenderLine((Span(truncate(text, width), "header"),))

    def _endpoint_line(self, row: EndpointRow, width: int, index: int) -> RenderLine:
        selected = index == self.selected
        style = (
            "selected" if selected else NOVELTY_STYLES.get(row.row.novelty.level, "")
        )
        badge = self._novelty_badge(row.row.novelty)
        prefix = (
            f"{row.socket.proto:<5} {row.socket.local:<22} "
            f"{(row.socket.remote or '-'):<22} {row.socket.state:<10} "
            f"{row.exposure:<7} {row.row.process.pid:>7} {row.row.user:<8} "
            f"{badge:<5} "
        )
        command = truncate(row.display_command, max(1, width - len(prefix)))
        spans = [Span(prefix, style)]
        spans.append(Span(command, "selected" if selected else ""))
        return RenderLine(tuple(spans), row_index=index)

    def _cgroup_header(self, width: int) -> RenderLine:
        text = (
            f"{'NAME':<22} {'PROCS':>5} {'NOV':<5} {'WR/s':>8} {'TX/s':>8} "
            f"{'CPU':>5} {'MEM':>6} {'USER':<8} PROCESSES"
        )
        return RenderLine((Span(truncate(text, width), "header"),))

    def _cgroup_line(self, row: CgroupRow, width: int, index: int) -> RenderLine:
        selected = index == self.selected
        style = "selected" if selected else NOVELTY_STYLES.get(row.novelty.level, "")
        badge = self._novelty_badge(row.novelty)
        prefix = (
            f"{truncate(row.name, 22):<22} {row.count:>5} {badge:<5} "
            f"{format_rate(row.write_rate):>8} {format_rate(row.tx_rate):>8} "
            f"{row.cpu_percent:>4.0f}% {format_bytes(row.rss):>6} "
            f"{','.join(row.users)[:8]:<8} "
        )
        comms = truncate(",".join(row.comms), max(1, width - len(prefix)))
        spans = [Span(prefix, style)]
        spans.append(Span(comms, "selected" if selected else ""))
        return RenderLine(tuple(spans), row_index=index)

    def _event_lines(self, width: int) -> list[RenderLine]:
        lines = [
            RenderLine(
                (
                    Span(
                        f"{'TIME':<8} {'LEVEL':<9} {'PID':>7} {'PROCESS':<20} WHY",
                        "header",
                    ),
                )
            )
        ]
        for event in self.events:
            stamp = dt.datetime.fromtimestamp(event.ts).strftime("%H:%M:%S")
            level = event.level
            style = NOVELTY_STYLES.get(level, "")
            text = (
                f"{stamp:<8} {level:<9} {event.pid:>7} "
                f"{truncate(event.comm, 20):<20} {truncate(event.reasons, max(1, width - 48))}"
            )
            lines.append(RenderLine((Span(text[:width], style),)))
        if len(lines) == 1:
            lines.append(RenderLine((Span("no events recorded yet", "dim"),)))
        return lines

    def detail_lines(self, item: Any, view: str | None = None) -> list[tuple[str, str]]:
        """Untruncated detail lines for the selected item."""
        view = self.view if view is None else view
        if isinstance(item, ViewRow):
            return self._detail_process(item, view)
        if isinstance(item, CommandRow):
            return self._detail_command(item)
        if isinstance(item, EndpointRow):
            return self._detail_endpoint(item)
        if isinstance(item, CgroupRow):
            return self._detail_cgroup(item)
        if isinstance(item, Event):
            return self._detail_event(item)
        return []

    def _detail_process(self, row: ViewRow, view: str) -> list[tuple[str, str]]:
        process = row.process
        cgroup = process.cgroup or ""
        seen = (
            f"first seen {format_age(self.snapshot_ts - row.first_seen)} ago"
            if row.first_seen
            else "not in baseline yet"
        )
        identity = (
            f"PID {process.pid}  {process.comm}  uid {process.uid}({row.user})  "
            f"{row.category}  {row.novelty.level} {row.novelty.score}  perm {row.perm}  "
            f"{seen}, {row.observations} obs"
        )
        lines: list[tuple[str, str]] = [(identity, "bold")]
        reasons = "; ".join(row.novelty.reasons) or "no baseline deviation"
        lines.append(
            (
                "why: " + reasons,
                "warn" if row.novelty.score else "dim",
            )
        )
        if view == "risk":
            lines.append(
                ("risk: " + ", ".join(risk_reasons(process, self.config)), "warn")
            )
        profile = self.profiles.get(process.fingerprint)
        if profile is not None:
            ports = ", ".join(f":{port}" for port in sorted(profile.ports)) or "none"
            caps = ", ".join(sorted(profile.caps)) or "none"
            lines.append(
                (
                    (
                        f"baseline: {profile.observations} obs | sockets mean "
                        f"{profile.sockets_mean:.1f} | write {format_rate(profile.write_mean)} | "
                        f"cpu {profile.cpu_mean:.0f}% | ports {ports} | caps {caps}"
                    ),
                    "dim",
                )
            )
        else:
            lines.append(("baseline: not seen yet", "dim"))
        remotes = ", ".join(sorted(process.remote_endpoints)) or "none"
        lines.append(
            (
                (
                    f"sockets: {row.conn_count} inet ({row.listen_count} listening), "
                    f"{len(process.unix_sockets)} unix, {row.remote_count} remotes ({remotes})"
                ),
                "",
            )
        )
        lines.append(
            (
                (
                    f"io: write {format_rate(row.write_rate)} read "
                    f"{format_rate(row.read_rate)} | cpu {row.cpu_percent:.0f}% | "
                    f"tx {format_rate(row.tx_rate)} rx {format_rate(row.rx_rate)} | "
                    f"rss {format_bytes(row.rss)} | {process.threads} threads"
                ),
                "",
            )
        )
        caps = ", ".join(sorted(process.caps)) or "none"
        lines.append(
            (
                (
                    f"files {process.open_files} ({process.open_writes} writable) | "
                    f"caps: {caps} | seccomp {process.seccomp} | "
                    f"no_new_privs {process.no_new_privs}"
                ),
                "dim",
            )
        )
        exe = process.exe or f"[{process.comm}]"
        if process.exe_deleted:
            exe += " (deleted)"
        lines.append((f"exe: {exe}", "dim"))
        lines.append((f"cgroup: {cgroup or '(none)'}", "dim"))
        if process.started_at:
            lines.append((f"started: {_iso(process.started_at)}", "dim"))
        lines.append((f"cmd: {process.cmdline or f'[{process.comm}]'}", "dim"))
        return lines

    def _detail_command(self, row: CommandRow) -> list[tuple[str, str]]:
        best = max(row.members, key=lambda member: member.novelty.score)
        pids = ", ".join(str(pid) for pid in row.pids[:12])
        if len(row.pids) > 12:
            pids += ", …"
        lines: list[tuple[str, str]] = [
            (
                (
                    f"{row.comm}  {row.count} process(es)  pids {pids}  "
                    f"users {', '.join(row.users)}"
                ),
                "bold",
            ),
            (
                (
                    f"{row.novelty.level} {row.novelty.score}  {row.category}  "
                    f"perm {row.perm}  tags {','.join(row.tags) or '-'}"
                ),
                "",
            ),
            (
                "why: " + ("; ".join(row.novelty.reasons) or "no baseline deviation"),
                "warn" if row.novelty.score else "dim",
            ),
            (
                (
                    f"totals: conn {row.conn_count} ({row.listen_count} listening) | "
                    f"write {format_rate(row.write_rate)} | tx {format_rate(row.tx_rate)} | "
                    f"cpu {row.cpu_percent:.0f}% | rss {format_bytes(row.rss)}"
                ),
                "",
            ),
        ]
        profile = self.profiles.get(row.fingerprint)
        if profile is not None:
            ports = ", ".join(f":{port}" for port in sorted(profile.ports)) or "none"
            lines.append(
                (
                    (
                        f"baseline: {profile.observations} obs | sockets mean "
                        f"{profile.sockets_mean:.1f} | write {format_rate(profile.write_mean)} | "
                        f"cpu {profile.cpu_mean:.0f}% | ports {ports}"
                    ),
                    "dim",
                )
            )
        else:
            lines.append(("baseline: not seen yet", "dim"))
        lines.append((f"cmd: {best.display_command}", "dim"))
        for member in row.members[:20]:
            lines.append(
                (
                    (
                        f"  pid {member.process.pid}  {member.user}  "
                        f"{member.novelty.level} {member.novelty.score}  "
                        f"{member.category}"
                    ),
                    "dim",
                )
            )
        return lines

    def _detail_endpoint(self, row: EndpointRow) -> list[tuple[str, str]]:
        sock = row.socket
        process = row.row.process
        lines: list[tuple[str, str]] = [
            (
                (
                    f"{sock.proto.upper()}  {sock.local or '-'} -> "
                    f"{sock.remote or '-'}  {sock.state}  exposure {row.exposure}"
                ),
                "bold",
            ),
            (
                (
                    f"pid {process.pid}  {process.comm}  user {row.row.user}  "
                    f"{row.row.novelty.level} {row.row.novelty.score}  "
                    f"perm {row.row.perm}"
                ),
                "",
            ),
            (
                "why: "
                + ("; ".join(row.row.novelty.reasons) or "no baseline deviation"),
                "warn" if row.row.novelty.score else "dim",
            ),
            (
                (
                    f"caps: {', '.join(sorted(process.caps)) or 'none'} | "
                    f"seccomp {process.seccomp}"
                ),
                "dim",
            ),
            (f"cmd: {process.cmdline or f'[{process.comm}]'}", "dim"),
        ]
        return lines

    def _detail_cgroup(self, row: CgroupRow) -> list[tuple[str, str]]:
        lines: list[tuple[str, str]] = [
            (f"cgroup: {row.path}", "bold"),
            (
                (
                    f"{row.count} process(es)  users {', '.join(row.users)}  "
                    f"{row.novelty.level} {row.novelty.score}"
                ),
                "",
            ),
            (
                "why: " + ("; ".join(row.novelty.reasons) or "no baseline deviation"),
                "warn" if row.novelty.score else "dim",
            ),
            (
                (
                    f"totals: write {format_rate(row.write_rate)} | "
                    f"tx {format_rate(row.tx_rate)} | cpu {row.cpu_percent:.0f}% | "
                    f"rss {format_bytes(row.rss)}"
                ),
                "",
            ),
            (f"processes: {', '.join(row.comms)}", "dim"),
        ]
        for member in row.members[:20]:
            lines.append(
                (
                    (
                        f"  pid {member.process.pid}  {member.process.comm}  "
                        f"{member.user}  {member.novelty.level} {member.novelty.score}"
                    ),
                    "dim",
                )
            )
        return lines

    def _detail_event(self, event: Event) -> list[tuple[str, str]]:
        stamp = dt.datetime.fromtimestamp(event.ts).strftime("%Y-%m-%d %H:%M:%S")
        return [
            (
                f"{event.level}  pid {event.pid}  {event.comm}  {stamp}",
                "bold",
            ),
            ("why: " + (event.reasons or "no reason recorded"), "warn"),
            (f"fingerprint: {event.fingerprint}", "dim"),
        ]

    def _detail_lines(self, width: int) -> list[RenderLine]:
        if self.view == "events":
            return [
                RenderLine((Span(f"{len(self.events)} recent baseline events", "dim"),))
            ]
        item = self.selected_item()
        if item is None:
            message = {
                "commands": "no commands match the filter",
                "network": "no sockets match the filter",
                "cgroups": "no cgroups match the filter",
                "risk": "no risky processes",
            }.get(self.view, "no process selected")
            return [RenderLine((Span(message, "dim"),))]
        return [
            RenderLine((Span(truncate(text, width), style),))
            for text, style in self.detail_lines(item)
        ]

    def _footer_line(self, width: int) -> RenderLine:
        if self.input_mode:
            text = f"filter: {self.filter_buffer}_  (enter apply, esc cancel)"
            return RenderLine((Span(truncate(text, width), "accent"),))
        text = (
            "1-7 views  j/k move  s/S sort  n novelty  t tree  w compact  "
            "enter details  y copy  r refresh  R auto  / filter  ? help  q quit"
        )
        if self.view in ("all", "risk", "commands", "network", "cgroups"):
            text += f"  |  sort {SORT_LABELS[self.sort_key]} {'desc' if self.sort_reverse else 'asc'}"
        return RenderLine((Span(truncate(text, width), "dim"),))


# ---------------------------------------------------------------------------
# Textual TUI (optional; direct execution uses uv + inline dependency)
# ---------------------------------------------------------------------------


RICH_STYLE_NAMES = {
    "warn": "yellow",
    "label": "yellow",
    "accent": "cyan",
    "title": "bold cyan",
    "header": "bold",
    "selected": "reverse",
    "new": "bold red",
    "changed": "yellow",
    "returning": "magenta",
    "rare": "cyan",
}


def _rich_style(style: str) -> str:
    """Translate the plain renderer's style names for rich.text.Text."""
    return RICH_STYLE_NAMES.get(style, style)


def _textual_is_modern() -> bool:
    try:
        from importlib.metadata import PackageNotFoundError, version

        major = int(version("textual").split(".", 1)[0])
    except (PackageNotFoundError, ValueError):
        return False
    return major >= 1


TEXTUAL_AVAILABLE = False
if _textual_is_modern():
    try:
        from rich.text import Text as RichText
        from textual.app import App, ComposeResult
        from textual.binding import Binding, BindingType
        from textual.containers import VerticalScroll
        from textual.screen import ModalScreen
        from textual.timer import Timer
        from textual.widgets import (
            DataTable,
            Footer,
            Input,
            Static,
            TabbedContent,
            TabPane,
        )

        TEXTUAL_AVAILABLE = True
    except ImportError:  # pragma: no cover - depends on environment
        LOG.debug("textual import failed", exc_info=True)


if TEXTUAL_AVAILABLE:

    class ProcTable(DataTable):
        """DataTable that scrolls one whole column per left/right press.

        With a row cursor, Textual scrolls horizontally one cell at a time,
        which makes wide process tables feel stuck. Aligning to column
        boundaries moves exactly one column per keypress instead.
        """

        def column_offsets(self) -> list[int]:
            """Scroll offsets where each scrollable column starts."""
            offsets = [0]
            total = 0
            for column in self.ordered_columns[self.fixed_columns :]:
                total += column.get_render_width(self)
                offsets.append(total)
            return offsets

        def scroll_column(self, direction: int) -> None:
            """Scroll to the previous or next column boundary."""
            offsets = self.column_offsets()
            current = self.scroll_x
            if direction > 0:
                candidates = [offset for offset in offsets if offset > current]
                target = candidates[0] if candidates else offsets[-1]
            else:
                candidates = [offset for offset in offsets if offset < current]
                target = candidates[-1] if candidates else 0
            self.scroll_to(x=target, animate=False, force=True)

        def action_cursor_left(self) -> None:
            if self.show_cursor and self.cursor_type in ("cell", "column"):
                super().action_cursor_left()
            else:
                self.scroll_column(-1)

        def action_cursor_right(self) -> None:
            if self.show_cursor and self.cursor_type in ("cell", "column"):
                super().action_cursor_right()
            else:
                self.scroll_column(1)

    HELP_ROWS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
        (
            "VIEWS",
            (
                ("1", "Triage"),
                ("2", "All processes"),
                ("3", "Events"),
                ("4", "Commands (grouped by identity)"),
                ("5", "Network sockets"),
                ("6", "Cgroups"),
                ("7 / !", "Risk (root, caps, deleted exe, suspicious path)"),
            ),
        ),
        (
            "MOVE",
            (
                ("j / down", "Next item"),
                ("k / up", "Previous item"),
                ("left / right", "Previous / next column"),
                ("g / G", "Top / bottom"),
                ("[ / ]", "Previous / next group (triage)"),
            ),
        ),
        (
            "SORT",
            (
                ("s", "Next sort column (includes AGE)"),
                ("S", "Reverse sort order"),
                ("click header", "Sort by that column"),
            ),
        ),
        (
            "FILTER",
            (
                ("/", "Filter by pid, name, user, category, capability"),
                ("n", "Cycle novelty: all, NEW, CHANGED, RARE, RETURNING"),
                ("c", "Clear filter and novelty filter"),
                ("esc", "Cancel filter entry"),
            ),
        ),
        (
            "DISPLAY",
            (
                ("t", "Toggle process tree in All processes"),
                ("w", "Toggle compact / wide columns"),
                ("enter", "Full detail screen"),
                ("y", "Copy selected pid/command"),
            ),
        ),
        (
            "SAMPLING",
            (
                ("r", "Refresh now"),
                ("R", "Toggle auto-refresh"),
                ("+ / -", "Adjust auto-refresh interval"),
                ("q", "Quit"),
                ("?", "Close this help"),
            ),
        ),
    )

    class HelpScreen(ModalScreen[None]):
        """Full keyboard shortcut reference, usable on narrow screens."""

        CSS = """
        HelpScreen { align: center middle; background: $background 60%; }
        #help {
            width: 72;
            max-width: 95%;
            height: auto;
            max-height: 90%;
            padding: 1 2;
            border: round $accent;
            background: $surface;
        }
        """

        BINDINGS: ClassVar[list[BindingType]] = [
            Binding("escape", "dismiss", "Close", show=False),
            Binding("question_mark", "dismiss", "Close", show=False),
            Binding("q", "dismiss", "Close", show=False),
        ]

        def compose(self) -> ComposeResult:
            with VerticalScroll(id="help", can_focus=True):
                yield Static(self._help_text())

        def on_mount(self) -> None:
            self.query_one(VerticalScroll).focus()

        @staticmethod
        def _help_text() -> RichText:
            text = RichText()
            text.append("procwatch keyboard shortcuts\n", style="bold cyan")
            for title, entries in HELP_ROWS:
                text.append(f"\n{title}\n", style="bold")
                for keys, description in entries:
                    text.append(f"  {keys:<14}", style="cyan")
                    text.append(f"{description}\n")
            text.append("\nesc or ? closes this help", style="dim")
            return text

    class DetailScreen(ModalScreen[None]):
        """Scrollable, untruncated detail for the selected row."""

        CSS = """
        DetailScreen { align: center middle; background: $background 60%; }
        #detail-modal {
            width: 100;
            max-width: 95%;
            height: auto;
            max-height: 90%;
            padding: 1 2;
            border: round $accent;
            background: $surface;
        }
        """

        BINDINGS: ClassVar[list[BindingType]] = [
            Binding("escape", "dismiss", "Close", show=False),
            Binding("q", "dismiss", "Close", show=False),
            Binding("question_mark", "dismiss", "Close", show=False),
        ]

        def __init__(self, text: RichText) -> None:
            super().__init__()
            self.text = text

        def compose(self) -> ComposeResult:
            with VerticalScroll(id="detail-modal", can_focus=True):
                yield Static(self.text)

        def on_mount(self) -> None:
            self.query_one(VerticalScroll).focus()

    class ProcWatchApp(App[None]):
        """Interactive Textual dashboard."""

        CSS = """
        Screen { layout: vertical; }
        #summary { height: 2; padding: 0 1; background: $boost; }
        TabbedContent { height: 1fr; }
        TabPane { height: 1fr; }
        DataTable { height: 1fr; }
        #filter { height: 3; margin: 0 1; display: none; }
        #detail { height: 6; padding: 0 1; border-top: solid $accent; }
        Footer { height: 1; }
        """
        ENABLE_COMMAND_PALETTE = False
        BINDINGS: ClassVar[list[BindingType]] = [
            Binding("q", "quit", "Quit"),
            Binding("1", "show_main", "Triage"),
            Binding("2", "show_all", "All"),
            Binding("3", "show_events", "Events"),
            Binding("4", "show_commands", "Commands"),
            Binding("5", "show_network", "Network"),
            Binding("6", "show_cgroups", "Cgroups"),
            Binding("7", "show_risk", "Risk"),
            Binding("exclamation_mark", "show_risk", "Risk", show=False),
            Binding("j", "cursor_down", "Down", show=False),
            Binding("k", "cursor_up", "Up", show=False),
            Binding("g", "top", "Top", show=False),
            Binding("G", "bottom", "Bottom", show=False),
            Binding("left_square_bracket", "group_prev", "Prev group", show=False),
            Binding("right_square_bracket", "group_next", "Next group", show=False),
            Binding("s", "sort_next", "Sort"),
            Binding("S", "sort_reverse", "Reverse"),
            Binding("n", "novelty_filter", "Novelty"),
            Binding("t", "toggle_tree", "Tree"),
            Binding("w", "toggle_compact", "Compact"),
            Binding("enter", "details", "Details"),
            Binding("y", "copy", "Copy"),
            Binding("slash", "filter", "Filter"),
            Binding("c", "clear_filter", "Clear filter", show=False),
            Binding("r", "refresh_data", "Refresh"),
            Binding("R", "toggle_auto_refresh", "Auto refresh"),
            Binding("plus", "interval_up", "Interval +", show=False),
            Binding("equals_sign", "interval_up", "Interval +", show=False),
            Binding("minus", "interval_down", "Interval -", show=False),
            Binding("question_mark", "help", "Help"),
            Binding("escape", "cancel_filter", "Cancel", show=False),
        ]
        VIEW_BY_PANE: ClassVar[dict[str, str]] = {
            "tab-main": "main",
            "tab-all": "all",
            "tab-events": "events",
            "tab-commands": "commands",
            "tab-network": "network",
            "tab-cgroups": "cgroups",
            "tab-risk": "risk",
        }
        TABLE_BY_VIEW: ClassVar[dict[str, str]] = {
            "main": "table-main",
            "all": "table-all",
            "events": "table-events",
            "commands": "table-commands",
            "network": "table-network",
            "cgroups": "table-cgroups",
            "risk": "table-risk",
        }
        HEADER_SORT: ClassVar[dict[str, str]] = {
            "CONN": "connections",
            "PERM": "perm",
            "WR/s": "write",
            "TX/s": "tx",
            "CPU": "cpu",
            "MEM": "mem",
            "NOV": "novelty",
            "PID": "pid",
        }
        PROCESS_COLUMNS: ClassVar[tuple[tuple[str, str, int], ...]] = (
            ("CAT", "cat", 9),
            ("PID", "pid", 7),
            ("NOV", "nov", 5),
            ("CONN", "conn", 6),
            ("PERM", "perm", 4),
            ("WR/s", "wr", 8),
            ("TX/s", "tx", 8),
            ("CPU", "cpu", 5),
            ("MEM", "mem", 6),
            ("TAGS", "tags", 20),
            ("USER", "user", 9),
            ("COMMAND", "command", 40),
        )
        PROCESS_COMPACT_COLUMNS: ClassVar[tuple[tuple[str, str, int], ...]] = (
            ("PID", "pid", 7),
            ("NOV", "nov", 5),
            ("CONN", "conn", 6),
            ("WR/s", "wr", 8),
            ("COMMAND", "command", 40),
        )
        COMMAND_COLUMNS: ClassVar[tuple[tuple[str, str, int], ...]] = (
            ("COUNT", "count", 5),
            ("NOV", "nov", 5),
            ("CONN", "conn", 6),
            ("PERM", "perm", 4),
            ("WR/s", "wr", 8),
            ("TX/s", "tx", 8),
            ("CPU", "cpu", 5),
            ("MEM", "mem", 6),
            ("TAGS", "tags", 20),
            ("USER", "user", 9),
            ("COMMAND", "command", 40),
        )
        COMMAND_COMPACT_COLUMNS: ClassVar[tuple[tuple[str, str, int], ...]] = (
            ("COUNT", "count", 5),
            ("NOV", "nov", 5),
            ("CONN", "conn", 6),
            ("WR/s", "wr", 8),
            ("COMMAND", "command", 40),
        )
        CGROUP_COLUMNS: ClassVar[tuple[tuple[str, str, int], ...]] = (
            ("NAME", "name", 22),
            ("PROCS", "count", 5),
            ("NOV", "nov", 5),
            ("WR/s", "wr", 8),
            ("TX/s", "tx", 8),
            ("CPU", "cpu", 5),
            ("MEM", "mem", 6),
            ("USER", "user", 9),
            ("PROCESSES", "procs", 30),
        )
        CGROUP_COMPACT_COLUMNS: ClassVar[tuple[tuple[str, str, int], ...]] = (
            ("NAME", "name", 22),
            ("PROCS", "count", 5),
            ("NOV", "nov", 5),
            ("WR/s", "wr", 8),
            ("PROCESSES", "procs", 30),
        )
        ENDPOINT_COLUMNS: ClassVar[tuple[tuple[str, str, int], ...]] = (
            ("PROTO", "proto", 5),
            ("LOCAL", "local", 22),
            ("REMOTE", "remote", 22),
            ("STATE", "state", 10),
            ("EXPOSE", "exposure", 7),
            ("PID", "pid", 7),
            ("USER", "user", 9),
            ("NOV", "nov", 5),
            ("COMMAND", "command", 30),
        )
        ENDPOINT_COMPACT_COLUMNS: ClassVar[tuple[tuple[str, str, int], ...]] = (
            ("LOCAL", "local", 22),
            ("REMOTE", "remote", 22),
            ("EXPOSE", "exposure", 7),
            ("PID", "pid", 7),
            ("COMMAND", "command", 30),
        )
        EVENT_COLUMNS: ClassVar[tuple[tuple[str, str, int], ...]] = (
            ("TIME", "time", 14),
            ("LEVEL", "level", 9),
            ("PID", "pid", 7),
            ("PROCESS", "process", 20),
            ("WHY", "why", 40),
        )

        def __init__(self, dashboard: Dashboard, *, auto_poll: bool = False) -> None:
            super().__init__()
            self.dashboard = dashboard
            self.auto_poll = auto_poll
            self.compact = False
            self.refresh_timer: Timer | None = None
            self.rows_by_key: dict[str, ViewRow] = {}
            self.events_by_key: dict[str, Event] = {}
            self.commands_by_key: dict[str, CommandRow] = {}
            self.endpoints_by_key: dict[str, EndpointRow] = {}
            self.cgroups_by_key: dict[str, CgroupRow] = {}
            self.selected_keys: dict[str, str] = {}
            self.selected_groups: dict[str, str] = {}
            self.row_groups: dict[str, dict[str, str]] = {}
            self.ready = False

        def compose(self) -> ComposeResult:
            yield Static(id="summary")
            with TabbedContent(initial="tab-main"):
                with TabPane("Triage", id="tab-main"):
                    yield ProcTable(
                        id="table-main",
                        cursor_type="row",
                        zebra_stripes=True,
                        fixed_columns=1,
                    )
                with TabPane("All processes", id="tab-all"):
                    yield ProcTable(
                        id="table-all",
                        cursor_type="row",
                        zebra_stripes=True,
                        fixed_columns=1,
                    )
                with TabPane("Events", id="tab-events"):
                    yield ProcTable(
                        id="table-events", cursor_type="row", zebra_stripes=True
                    )
                with TabPane("Commands", id="tab-commands"):
                    yield ProcTable(
                        id="table-commands", cursor_type="row", zebra_stripes=True
                    )
                with TabPane("Network", id="tab-network"):
                    yield ProcTable(
                        id="table-network", cursor_type="row", zebra_stripes=True
                    )
                with TabPane("Cgroups", id="tab-cgroups"):
                    yield ProcTable(
                        id="table-cgroups", cursor_type="row", zebra_stripes=True
                    )
                with TabPane("Risk", id="tab-risk"):
                    yield ProcTable(
                        id="table-risk", cursor_type="row", zebra_stripes=True
                    )
            yield Input(
                placeholder="filter by pid, name, user, category, capability",
                id="filter",
            )
            yield Static(id="detail")
            yield Footer()

        def on_mount(self) -> None:
            self.configure_tables()
            self.query_one("#filter", Input).display = False
            self.ready = True
            if self.dashboard.snapshot is None:
                self.dashboard.poll()
            self.refresh_views()
            self.call_after_refresh(self.focus_table)
            self.apply_auto_refresh()

        def columns_for(self, view: str) -> tuple[tuple[str, str, int], ...]:
            if view in ("main", "all", "risk"):
                return (
                    self.PROCESS_COMPACT_COLUMNS
                    if self.compact
                    else self.PROCESS_COLUMNS
                )
            if view == "commands":
                return (
                    self.COMMAND_COMPACT_COLUMNS
                    if self.compact
                    else self.COMMAND_COLUMNS
                )
            if view == "cgroups":
                return (
                    self.CGROUP_COMPACT_COLUMNS if self.compact else self.CGROUP_COLUMNS
                )
            if view == "network":
                return (
                    self.ENDPOINT_COMPACT_COLUMNS
                    if self.compact
                    else self.ENDPOINT_COLUMNS
                )
            return self.EVENT_COLUMNS

        def configure_tables(self) -> None:
            for view, table_id in self.TABLE_BY_VIEW.items():
                table = self.query_one(f"#{table_id}", DataTable)
                table.clear(columns=True)
                for label, key, width in self.columns_for(view):
                    table.add_column(label, key=key, width=width)

        def tick(self) -> None:
            if not self.auto_poll:
                return
            self.dashboard.poll()
            self.refresh_views()

        def apply_auto_refresh(self) -> None:
            """Start or stop the periodic sampling timer."""
            if self.auto_poll:
                if self.refresh_timer is None:
                    self.refresh_timer = self.set_interval(
                        self.dashboard.config.interval, self.tick
                    )
            elif self.refresh_timer is not None:
                self.refresh_timer.stop()
                self.refresh_timer = None

        # -- view plumbing ---------------------------------------------
        def active_table_id(self) -> str:
            return self.TABLE_BY_VIEW[self.dashboard.view]

        def active_table(self) -> DataTable:
            return self.query_one(f"#{self.active_table_id()}", DataTable)

        def focus_table(self) -> None:
            if self.ready:
                self.active_table().focus()

        def refresh_views(self, *, preserve_scroll: bool = True) -> None:
            if not self.ready:
                return
            self.update_summary()
            view = self.dashboard.view
            if view == "main":
                table = self.query_one("#table-main", DataTable)
                labelled = []
                for group_name, rows in self.dashboard.grouped_rows():
                    short = (
                        "NOVEL"
                        if group_name == GROUP_NOVEL
                        else CATEGORY_SHORT[rows[0].category]
                    )
                    labelled.extend((short, row) for row in rows)
                self.fill_process_table(
                    table, view, labelled, preserve_scroll=preserve_scroll
                )
            elif view in ("all", "risk"):
                table_id = "table-all" if view == "all" else "table-risk"
                table = self.query_one(f"#{table_id}", DataTable)
                rows = self.dashboard.visible_items()
                label = (
                    CATEGORY_SHORT[row.category] if view == "all" else "RISK"
                    for row in rows
                )
                self.fill_process_table(
                    table,
                    view,
                    list(zip(label, rows)),
                    preserve_scroll=preserve_scroll,
                )
            elif view == "commands":
                self.fill_commands(
                    self.query_one("#table-commands", DataTable),
                    self.dashboard.visible_items(),
                    preserve_scroll=preserve_scroll,
                )
            elif view == "network":
                self.fill_endpoints(
                    self.query_one("#table-network", DataTable),
                    self.dashboard.visible_items(),
                    preserve_scroll=preserve_scroll,
                )
            elif view == "cgroups":
                self.fill_cgroups(
                    self.query_one("#table-cgroups", DataTable),
                    self.dashboard.visible_items(),
                    preserve_scroll=preserve_scroll,
                )
            else:
                self.fill_events(
                    self.query_one("#table-events", DataTable),
                    preserve_scroll=preserve_scroll,
                )
            self.update_detail()

        def write_table(
            self,
            table: DataTable,
            entries: Sequence[tuple[str, Mapping[str, Any]]],
            columns: Sequence[tuple[str, str, int]],
            *,
            preserve_scroll: bool,
        ) -> None:
            """Replace table rows, keeping cursor row and scroll when possible."""
            scroll_x = table.scroll_x
            scroll_y = table.scroll_y
            first_key = self.selected_keys.get(table.id, "")
            keys: list[str] = []
            with self.batch_update():
                table.clear(columns=False)
                for key, cells in entries:
                    keys.append(key)
                    table.add_row(
                        *(cells.get(column_key, "") for _, column_key, _ in columns),
                        key=key,
                    )
            keep_selection = first_key in keys
            if not keep_selection:
                first_key = keys[0] if keys else ""
            self.selected_keys[table.id] = first_key
            index = keys.index(first_key) if first_key in keys else 0
            if table.row_count:
                target = max(0, min(index, table.row_count - 1))
                if preserve_scroll and keep_selection:
                    table.move_cursor(row=target, scroll=False)
                    table.scroll_to(x=scroll_x, y=scroll_y, animate=False)
                else:
                    table.move_cursor(row=target, scroll=True)

        def process_cells(self, category: str, row: ViewRow) -> dict[str, Any]:
            badge = {
                "NEW": "NEW",
                "CHANGED": "CHG",
                "RETURNING": "RET",
                "RARE": "RARE",
                "KNOWN": "",
            }.get(row.novelty.level, row.novelty.level[:4])
            style = {
                "NEW": "bold red",
                "CHANGED": "yellow",
                "RETURNING": "magenta",
                "RARE": "cyan",
                "KNOWN": "",
            }.get(row.novelty.level, "")
            command_style = "bold" if row.novelty.level in ("NEW", "CHANGED") else ""
            return {
                "cat": RichText(category, style="dim"),
                "pid": str(row.process.pid),
                "nov": RichText(badge, style=style),
                "conn": str(row.conn_count),
                "perm": str(row.perm),
                "wr": format_rate(row.write_rate),
                "tx": format_rate(row.tx_rate),
                "cpu": f"{row.cpu_percent:.0f}%",
                "mem": format_bytes(row.rss),
                "tags": ",".join(row.tags),
                "user": row.user,
                "command": RichText(
                    self.dashboard.display_command(row), style=command_style
                ),
            }

        def fill_process_table(
            self,
            table: DataTable,
            view: str,
            labelled_rows: Sequence[tuple[str, ViewRow]],
            *,
            preserve_scroll: bool = True,
        ) -> None:
            first_key = self.selected_keys.get(table.id, "")
            previous_group = self.selected_groups.get(table.id, "")
            self.rows_by_key = {}
            groups: dict[str, str] = {}
            entries: list[tuple[str, Mapping[str, Any]]] = []
            for category, row in labelled_rows:
                key = row.key
                groups[key] = category
                self.rows_by_key[key] = row
                entries.append((key, self.process_cells(category, row)))
            if first_key not in groups or groups.get(first_key) != previous_group:
                self.selected_keys[table.id] = ""
            self.write_table(
                table,
                entries,
                self.columns_for(view),
                preserve_scroll=preserve_scroll,
            )
            first_key = self.selected_keys.get(table.id, "")
            self.selected_groups[table.id] = groups.get(first_key, "")
            self.row_groups[table.id or ""] = groups

        def command_cells(self, row: CommandRow) -> dict[str, Any]:
            badge = {
                "NEW": "NEW",
                "CHANGED": "CHG",
                "RETURNING": "RET",
                "RARE": "RARE",
                "KNOWN": "",
            }.get(row.novelty.level, row.novelty.level[:4])
            style = {
                "NEW": "bold red",
                "CHANGED": "yellow",
                "RETURNING": "magenta",
                "RARE": "cyan",
                "KNOWN": "",
            }.get(row.novelty.level, "")
            return {
                "count": str(row.count),
                "nov": RichText(badge, style=style),
                "conn": str(row.conn_count),
                "perm": str(row.perm),
                "wr": format_rate(row.write_rate),
                "tx": format_rate(row.tx_rate),
                "cpu": f"{row.cpu_percent:.0f}%",
                "mem": format_bytes(row.rss),
                "tags": ",".join(row.tags),
                "user": ",".join(row.users),
                "command": RichText(
                    row.display_command,
                    style="bold" if row.novelty.level in ("NEW", "CHANGED") else "",
                ),
            }

        def fill_commands(
            self,
            table: DataTable,
            rows: Sequence[CommandRow],
            *,
            preserve_scroll: bool = True,
        ) -> None:
            self.commands_by_key = {row.key: row for row in rows}
            self.write_table(
                table,
                [(row.key, self.command_cells(row)) for row in rows],
                self.columns_for("commands"),
                preserve_scroll=preserve_scroll,
            )

        def cgroup_cells(self, row: CgroupRow) -> dict[str, Any]:
            badge = {
                "NEW": "NEW",
                "CHANGED": "CHG",
                "RETURNING": "RET",
                "RARE": "RARE",
                "KNOWN": "",
            }.get(row.novelty.level, row.novelty.level[:4])
            style = {
                "NEW": "bold red",
                "CHANGED": "yellow",
                "RETURNING": "magenta",
                "RARE": "cyan",
                "KNOWN": "",
            }.get(row.novelty.level, "")
            return {
                "name": row.name,
                "count": str(row.count),
                "nov": RichText(badge, style=style),
                "wr": format_rate(row.write_rate),
                "tx": format_rate(row.tx_rate),
                "cpu": f"{row.cpu_percent:.0f}%",
                "mem": format_bytes(row.rss),
                "user": ",".join(row.users),
                "procs": ",".join(row.comms),
            }

        def fill_cgroups(
            self,
            table: DataTable,
            rows: Sequence[CgroupRow],
            *,
            preserve_scroll: bool = True,
        ) -> None:
            self.cgroups_by_key = {row.key: row for row in rows}
            self.write_table(
                table,
                [(row.key, self.cgroup_cells(row)) for row in rows],
                self.columns_for("cgroups"),
                preserve_scroll=preserve_scroll,
            )

        def endpoint_cells(self, row: EndpointRow) -> dict[str, Any]:
            badge = {
                "NEW": "NEW",
                "CHANGED": "CHG",
                "RETURNING": "RET",
                "RARE": "RARE",
                "KNOWN": "",
            }.get(row.row.novelty.level, row.row.novelty.level[:4])
            style = {
                "NEW": "bold red",
                "CHANGED": "yellow",
                "RETURNING": "magenta",
                "RARE": "cyan",
                "KNOWN": "",
            }.get(row.row.novelty.level, "")
            return {
                "proto": row.socket.proto,
                "local": row.socket.local or "-",
                "remote": row.socket.remote or "-",
                "state": row.socket.state,
                "exposure": row.exposure,
                "pid": str(row.row.process.pid),
                "user": row.row.user,
                "nov": RichText(badge, style=style),
                "command": RichText(
                    row.display_command,
                    style="bold" if row.row.novelty.level in ("NEW", "CHANGED") else "",
                ),
            }

        def fill_endpoints(
            self,
            table: DataTable,
            rows: Sequence[EndpointRow],
            *,
            preserve_scroll: bool = True,
        ) -> None:
            self.endpoints_by_key = {row.key: row for row in rows}
            self.write_table(
                table,
                [(row.key, self.endpoint_cells(row)) for row in rows],
                self.columns_for("network"),
                preserve_scroll=preserve_scroll,
            )

        def fill_events(
            self, table: DataTable, *, preserve_scroll: bool = True
        ) -> None:
            needle = self.dashboard.filter_text.strip().lower()
            events = [
                event
                for event in self.dashboard.events
                if not needle
                or needle
                in f"{event.pid} {event.comm} {event.level} {event.reasons}".lower()
            ]
            if self.dashboard.novelty_filter:
                events = [
                    event
                    for event in events
                    if event.level == self.dashboard.novelty_filter
                ]
            self.events_by_key = {}
            entries: list[tuple[str, Mapping[str, Any]]] = []
            for index, event in enumerate(events):
                key = f"{event.ts}:{event.pid}:{index}"
                self.events_by_key[key] = event
                style = {
                    "NEW": "bold red",
                    "CHANGED": "yellow",
                    "RETURNING": "magenta",
                    "RARE": "cyan",
                }.get(event.level, "")
                entries.append(
                    (
                        key,
                        {
                            "time": dt.datetime.fromtimestamp(event.ts).strftime(
                                "%m-%d %H:%M:%S"
                            ),
                            "level": RichText(event.level, style=style),
                            "pid": str(event.pid),
                            "process": event.comm,
                            "why": event.reasons,
                        },
                    )
                )
            self.write_table(
                table,
                entries,
                self.EVENT_COLUMNS,
                preserve_scroll=preserve_scroll,
            )

        def update_summary(self) -> None:
            totals = self.dashboard.totals()
            title = RichText()
            title.append("procwatch", style="bold cyan")
            title.append("  process baseline triage", style="dim")
            if self.auto_poll:
                title.append(
                    f"   auto {self.dashboard.config.interval:g}s", style="dim"
                )
            else:
                title.append("   manual", style="dim")
            title.append(
                f"   {dt.datetime.fromtimestamp(self.dashboard.snapshot_ts or time.time()).strftime('%H:%M:%S')}",
                style="dim",
            )
            if self.dashboard.warming:
                title.append("   baseline warming", style="yellow")
            metrics = RichText()
            metrics.append(
                f"{totals['processes']} procs | {totals['new']} new | "
                f"{totals['changed']} changed | {totals['rare']} rare | "
                f"{totals['sockets']} sockets | write {format_rate(totals['write_rate'])} | "
            )
            metrics.append(
                "tx " + format_rate(totals["tx_rate"])
                if totals["net_available"]
                else "tx n/a",
                style="dim",
            )
            metrics.append(f" | baseline {totals['identities']}")
            if self.dashboard.filter_text:
                metrics.append(
                    f' | filter "{self.dashboard.filter_text}"', style="cyan"
                )
            if self.dashboard.novelty_filter:
                metrics.append(
                    f" | novelty {self.dashboard.novelty_filter}", style="cyan"
                )
            if self.dashboard.view == "all" and self.dashboard.tree_mode:
                metrics.append(" | tree", style="cyan")
            if self.compact:
                metrics.append(" | compact", style="cyan")
            if self.dashboard.view in (
                "all",
                "risk",
                "commands",
                "network",
                "cgroups",
            ):
                metrics.append(
                    f" | sort {SORT_LABELS[self.dashboard.sort_key]} "
                    f"{'desc' if self.dashboard.sort_reverse else 'asc'}",
                    style="cyan",
                )
            if self.dashboard.last_error:
                metrics.append(f" | error: {self.dashboard.last_error}", style="red")
            self.query_one("#summary", Static).update(
                RichText("\n").join([title, metrics])
            )

        def item_for_view(self) -> Any | None:
            view = self.dashboard.view
            table = self.active_table()
            key = self.selected_keys.get(table.id, "")
            if view == "events":
                return self.events_by_key.get(key)
            if view == "commands":
                return self.commands_by_key.get(key)
            if view == "network":
                return self.endpoints_by_key.get(key)
            if view == "cgroups":
                return self.cgroups_by_key.get(key)
            return self.rows_by_key.get(key)

        def update_detail(self) -> None:
            detail = self.query_one("#detail", Static)
            width = max(24, (self.size.width or 120) - 4)
            item = self.item_for_view()
            if item is None:
                if self.dashboard.view == "events":
                    message = f"{len(self.events_by_key)} events"
                else:
                    message = "select a row"
                detail.update(RichText(message, style="dim"))
                return
            text = RichText()
            for index, (line, style) in enumerate(self.dashboard.detail_lines(item)):
                if index:
                    text.append("\n")
                text.append(truncate(line, width), style=_rich_style(style))
            detail.update(text)

        # -- events ------------------------------------------------------
        def on_tabbed_content_tab_activated(
            self, event: TabbedContent.TabActivated
        ) -> None:
            pane = getattr(event, "pane", None)
            pane_id = getattr(pane, "id", "") if pane is not None else ""
            view = self.VIEW_BY_PANE.get(pane_id)
            if view:
                self.dashboard.set_view(view)
                self.refresh_views(preserve_scroll=False)
                self.call_after_refresh(self.focus_table)

        def on_data_table_row_highlighted(
            self, event: DataTable.RowHighlighted
        ) -> None:
            key = getattr(event.row_key, "value", None)
            if key:
                table_id = event.data_table.id or ""
                self.selected_keys[table_id] = key
                self.selected_groups[table_id] = self.row_groups.get(table_id, {}).get(
                    key, ""
                )
            if event.data_table is self.active_table():
                self.update_detail()

        def on_data_table_header_selected(
            self, event: DataTable.HeaderSelected
        ) -> None:
            if event.data_table.id not in ("table-all", "table-risk"):
                return
            key = self.HEADER_SORT.get(event.label.plain)
            if not key:
                return
            if self.dashboard.sort_key == key:
                self.dashboard.toggle_reverse()
            else:
                self.dashboard.set_sort(key)
            self.refresh_views(preserve_scroll=False)

        def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
            self.action_details()

        def on_input_submitted(self, event: Input.Submitted) -> None:
            self.dashboard.set_filter(event.value)
            self.hide_filter()
            self.refresh_views(preserve_scroll=False)

        # -- actions -----------------------------------------------------
        def action_show_main(self) -> None:
            self.query_one(TabbedContent).active = "tab-main"

        def action_show_all(self) -> None:
            self.query_one(TabbedContent).active = "tab-all"

        def action_show_events(self) -> None:
            self.query_one(TabbedContent).active = "tab-events"

        def action_show_commands(self) -> None:
            self.query_one(TabbedContent).active = "tab-commands"

        def action_show_network(self) -> None:
            self.query_one(TabbedContent).active = "tab-network"

        def action_show_cgroups(self) -> None:
            self.query_one(TabbedContent).active = "tab-cgroups"

        def action_show_risk(self) -> None:
            self.query_one(TabbedContent).active = "tab-risk"

        def action_cursor_down(self) -> None:
            self.active_table().action_cursor_down()

        def action_cursor_up(self) -> None:
            self.active_table().action_cursor_up()

        def action_top(self) -> None:
            self.active_table().move_cursor(row=0)

        def action_bottom(self) -> None:
            table = self.active_table()
            if table.row_count:
                table.move_cursor(row=table.row_count - 1)

        def move_group(self, direction: int) -> None:
            if self.dashboard.view != "main":
                return
            table = self.active_table()
            groups = self.row_groups.get(table.id or "", {})
            if not groups:
                return
            current_key = self.selected_keys.get(table.id or "", "")
            if current_key not in groups:
                return
            group_order: list[tuple[str, str]] = []
            for key, group in groups.items():
                if not group_order or group_order[-1][0] != group:
                    group_order.append((group, key))
            current_group = groups[current_key]
            index = next(
                (
                    position
                    for position, (group, _) in enumerate(group_order)
                    if group == current_group
                ),
                0,
            )
            target = max(0, min(len(group_order) - 1, index + direction))
            target_key = group_order[target][1]
            row_index = list(groups).index(target_key)
            table.move_cursor(row=row_index, scroll=True)

        def action_group_prev(self) -> None:
            self.move_group(-1)

        def action_group_next(self) -> None:
            self.move_group(1)

        def show_all_if_needed(self) -> None:
            if self.dashboard.view != "all":
                self.dashboard.set_view("all")
                self.query_one(TabbedContent).active = "tab-all"

        def action_sort_next(self) -> None:
            if self.dashboard.view in ("main", "events"):
                self.show_all_if_needed()
            self.dashboard.cycle_sort(1)
            self.refresh_views(preserve_scroll=False)

        def action_sort_reverse(self) -> None:
            if self.dashboard.view in ("main", "events"):
                self.show_all_if_needed()
            self.dashboard.toggle_reverse()
            self.refresh_views(preserve_scroll=False)

        def action_novelty_filter(self) -> None:
            self.dashboard.cycle_novelty_filter()
            self.refresh_views(preserve_scroll=False)

        def action_toggle_tree(self) -> None:
            if self.dashboard.view != "all":
                self.show_all_if_needed()
                if not self.dashboard.tree_mode:
                    self.dashboard.toggle_tree()
            else:
                self.dashboard.toggle_tree()
            self.refresh_views(preserve_scroll=False)

        def action_toggle_compact(self) -> None:
            self.compact = not self.compact
            self.configure_tables()
            self.refresh_views(preserve_scroll=False)
            self.update_summary()

        def action_details(self) -> None:
            if isinstance(self.screen, DetailScreen):
                return
            item = self.item_for_view()
            if item is None:
                return
            text = RichText()
            for index, (line, style) in enumerate(self.dashboard.detail_lines(item)):
                if index:
                    text.append("\n")
                text.append(line, style=_rich_style(style))
            self.push_screen(DetailScreen(text))

        def copy_text(self) -> str:
            item = self.item_for_view()
            if isinstance(item, ViewRow):
                return f"{item.process.pid} {item.display_command}"
            if isinstance(item, CommandRow):
                pids = " ".join(str(pid) for pid in item.pids)
                return f"{item.comm} pids {pids} :: {item.display_command}"
            if isinstance(item, EndpointRow):
                sock = item.socket
                return (
                    f"{item.row.process.pid} {item.row.process.comm} "
                    f"{sock.local} -> {sock.remote or '-'}"
                )
            if isinstance(item, CgroupRow):
                return item.path
            if isinstance(item, Event):
                return f"{item.pid} {item.comm} {item.reasons}"
            return ""

        def action_copy(self) -> None:
            text = self.copy_text()
            if not text:
                return
            self.copy_to_clipboard(text)
            self.notify(f"copied: {truncate(text, 60)}")

        def adjust_interval(self, direction: int) -> None:
            interval = self.dashboard.config.interval
            step = 1.0 if interval >= 1.0 else 0.5
            new_interval = max(0.5, interval + direction * step)
            if new_interval == interval:
                return
            self.dashboard.config.interval = new_interval
            if self.auto_poll:
                if self.refresh_timer is not None:
                    self.refresh_timer.stop()
                    self.refresh_timer = None
                self.apply_auto_refresh()
            self.update_summary()

        def action_interval_up(self) -> None:
            self.adjust_interval(1)

        def action_interval_down(self) -> None:
            self.adjust_interval(-1)

        def action_refresh_data(self) -> None:
            self.dashboard.poll()
            self.refresh_views()

        def action_toggle_auto_refresh(self) -> None:
            self.auto_poll = not self.auto_poll
            self.apply_auto_refresh()
            self.update_summary()

        def action_help(self) -> None:
            self.push_screen(HelpScreen())

        def action_filter(self) -> None:
            field = self.query_one("#filter", Input)
            field.value = self.dashboard.filter_text
            field.display = True
            field.focus()

        def hide_filter(self) -> None:
            field = self.query_one("#filter", Input)
            field.display = False
            self.focus_table()

        def action_cancel_filter(self) -> None:
            self.hide_filter()

        def action_clear_filter(self) -> None:
            self.dashboard.set_filter("")
            self.dashboard.novelty_filter = ""
            self.refresh_views(preserve_scroll=False)


# ---------------------------------------------------------------------------
# Process lock, logging, CLI
# ---------------------------------------------------------------------------


class LockBusy(RuntimeError):
    pass


@contextmanager
def runtime_lock(path: Path):
    """Acquire an exclusive, non-blocking single-writer lock."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise LockBusy(str(path)) from exc
        yield
    finally:
        try:
            fcntl.flock(handle, fcntl.LOCK_UN)
        except OSError:
            pass
        os.close(handle)


def setup_logging(paths: Paths, verbose: int) -> Path:
    """Configure file logging and return the log path."""
    logger = logging.getLogger("procwatch")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.handlers.clear()
    try:
        handler = logging.handlers.RotatingFileHandler(
            paths.log, maxBytes=1_000_000, backupCount=2, encoding="utf-8"
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    except OSError:
        logger.addHandler(logging.NullHandler())
    return paths.log


def _iso(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def _row_payload(row: ViewRow) -> dict[str, Any]:
    process = row.process
    return {
        "pid": process.pid,
        "ppid": process.ppid,
        "uid": process.uid,
        "user": row.user,
        "comm": process.comm,
        "cmdline": process.cmdline,
        "exe": process.exe,
        "exe_deleted": process.exe_deleted,
        "category": row.category,
        "tags": list(row.tags),
        "novelty": {
            "score": row.novelty.score,
            "level": row.novelty.level,
            "reasons": list(row.novelty.reasons),
        },
        "connections": row.conn_count,
        "listening": row.listen_count,
        "unix_sockets": len(process.unix_sockets),
        "remotes": sorted(process.remote_endpoints)[:20],
        "permissions": row.perm,
        "caps": sorted(process.caps),
        "write_rate": round(row.write_rate, 1),
        "read_rate": round(row.read_rate, 1),
        "tx_rate": round(row.tx_rate, 1),
        "rx_rate": round(row.rx_rate, 1),
        "cpu_percent": round(row.cpu_percent, 1),
        "rss": row.rss,
        "threads": process.threads,
        "seccomp": process.seccomp,
        "open_files": process.open_files,
        "open_writes": process.open_writes,
        "fingerprint": process.fingerprint,
        "started_at": _iso(process.started_at) if process.started_at else "",
    }


def snapshot_payload(dashboard: Dashboard, limit: int, sort_key: str) -> dict[str, Any]:
    stats = dashboard.baseline.stats()
    rows = sort_rows(
        dashboard.filtered_rows(),
        sort_key,
        default_reverse(sort_key),
    )[:limit]
    return {
        "generated_at": _iso(dashboard.snapshot_ts),
        "baseline": {
            "path": str(dashboard.baseline.path),
            "identities": stats["identities"],
            "observations": stats["observations"],
            "events": stats["events"],
            "size": stats["size"],
        },
        "totals": dashboard.totals(),
        "processes": [_row_payload(row) for row in rows],
    }


def events_payload(events: Sequence[Event]) -> list[dict[str, Any]]:
    return [
        {
            "time": _iso(event.ts),
            "level": event.level,
            "pid": event.pid,
            "process": event.comm,
            "reasons": event.reasons,
            "fingerprint": event.fingerprint,
        }
        for event in events
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Process baseline and anomaly dashboard.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "XDG files:\n"
            "  $XDG_STATE_HOME/procwatch/baseline.db\n"
            "  $XDG_CONFIG_HOME/procwatch/config.toml\n"
            "  $XDG_RUNTIME_DIR/procwatch.lock\n"
            "\n"
            "TUI keys: 1-7 views (Triage/All/Events/Commands/Network/Cgroups/Risk),\n"
            "j/k move, s/S sort, n novelty, t tree, w compact, enter details, y copy,\n"
            "/ filter, r refresh, R auto-refresh, +/- interval, ? full key list, q quit.\n"
            "The TUI needs textual>=1; direct execution uses uv and the inline dependency.\n"
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"procwatch {__version__}"
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="debug logging"
    )
    parser.add_argument("--db", type=Path, help="override the baseline SQLite path")
    parser.add_argument("--config", type=Path, help="override the TOML config path")
    parser.add_argument("--interval", type=float, help="sampling interval in seconds")
    parser.add_argument(
        "--sort", choices=SORT_KEYS, default="novelty", help="snapshot sort key"
    )
    parser.add_argument(
        "--limit", type=int, default=40, help="snapshot/event row limit"
    )
    parser.add_argument(
        "--json", action="store_true", help="JSON output with --snapshot/--events"
    )
    parser.add_argument(
        "--no-record",
        action="store_true",
        help="do not update the baseline (with --snapshot)",
    )
    parser.add_argument(
        "--proc-root", type=Path, default=Path("/proc"), help=argparse.SUPPRESS
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--snapshot", action="store_true", help="print one snapshot and exit"
    )
    group.add_argument(
        "--events", action="store_true", help="print recorded events and exit"
    )
    group.add_argument(
        "--baseline", action="store_true", help="print baseline statistics"
    )
    group.add_argument(
        "--reset-baseline",
        action="store_true",
        help="delete baseline identities and events",
    )
    return parser


def _print_baseline(db: Path, config: Config) -> None:
    with Baseline(db, config) as store:
        stats = store.stats()
        first = _iso(stats["first_seen"]) if stats["first_seen"] else "never"
        last = _iso(stats["last_seen"]) if stats["last_seen"] else "never"
        print(f"db: {store.path}")
        print(f"identities: {stats['identities']}")
        print(f"observations: {stats['observations']}")
        print(f"events: {stats['events']}")
        print(f"first seen: {first}")
        print(f"last seen: {last}")
        print(f"size: {format_bytes(stats['size'])}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.limit < 1:
        parser.error("--limit must be at least 1")
    try:
        paths = xdg_paths().ensure()
    except OSError as exc:
        print(f"procwatch: cannot create XDG directories: {exc}", file=sys.stderr)
        return 2
    config_path = args.config or paths.config_file
    try:
        config = Config.load(config_path)
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        print(f"procwatch: cannot read {config_path}: {exc}", file=sys.stderr)
        return 2
    if args.interval is not None:
        config.interval = max(0.2, args.interval)
    db = args.db or paths.db
    setup_logging(paths, args.verbose)
    if args.verbose:
        print(f"procwatch: logging to {paths.log}", file=sys.stderr)

    if args.reset_baseline:
        try:
            with runtime_lock(paths.lock), Baseline(db, config) as store:
                store.reset()
                print(f"baseline reset: {store.path}")
        except LockBusy:
            print(f"procwatch: another instance holds {paths.lock}", file=sys.stderr)
            return 1
        return 0

    if args.baseline:
        _print_baseline(db, config)
        return 0

    if args.events:
        with Baseline(db, config) as store:
            events = store.recent_events(args.limit)
        if args.json:
            print(json.dumps(events_payload(events), indent=2))
        else:
            for event in events:
                stamp = _iso(event.ts)
                print(
                    f"{stamp}  {event.level:<9} pid {event.pid:<7} {event.comm:<20} {event.reasons}"
                )
        return 0

    if args.snapshot:
        try:
            with runtime_lock(paths.lock), Baseline(db, config) as store:
                procfs = Procfs(args.proc_root, use_ss=args.proc_root == Path("/proc"))
                dashboard = Dashboard(
                    procfs,
                    store,
                    config,
                    record=not args.no_record,
                )
                dashboard.poll()
                if args.json:
                    print(
                        json.dumps(
                            snapshot_payload(dashboard, args.limit, args.sort), indent=2
                        )
                    )
                else:
                    height = max(24, min(400, args.limit + 20))
                    dashboard.set_view("main")
                    for line in dashboard.render(140, height):
                        print(line.text)
        except LockBusy:
            print(f"procwatch: another instance holds {paths.lock}", file=sys.stderr)
            return 1
        return 0

    if not TEXTUAL_AVAILABLE:
        print(
            "procwatch: the TUI needs textual>=1.0. Run ./procwatch.py (uv installs it "
            "from the inline script metadata), or install textual and run with python3.",
            file=sys.stderr,
        )
        return 2
    try:
        with runtime_lock(paths.lock), Baseline(db, config) as store:
            procfs = Procfs(args.proc_root, use_ss=args.proc_root == Path("/proc"))
            dashboard = Dashboard(procfs, store, config)
            ProcWatchApp(dashboard).run()
    except LockBusy:
        print(f"procwatch: another instance holds {paths.lock}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
