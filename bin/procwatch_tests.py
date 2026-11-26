#!/usr/bin/env pytest
# SPDX-License-Identifier: WTFPL

"""Tests for procwatch.py."""

import asyncio
import json
import os
import socket as _socket
from pathlib import Path

import pytest

import procwatch
from procwatch import (
    Baseline,
    Config,
    Dashboard,
    NetBytes,
    Novelty,
    Process,
    Procfs,
    Profile,
    Rates,
    Socket,
    assess_novelty,
    build_rows,
    capability_names,
    categorize,
    decode_inet_addr,
    filter_rows,
    format_age,
    format_bytes,
    format_rate,
    group_rows,
    parse_net_table,
    parse_proc_stat,
    parse_ss_tcp_info,
    parse_unix_table,
    permission_score,
    process_fingerprint,
    sort_rows,
    truncate,
    xdg_paths,
)

os.chdir(os.path.dirname(__file__))


# ---------------------------------------------------------------------------
# fake /proc tree
# ---------------------------------------------------------------------------


def ipv4_hex(address: str) -> str:
    return _socket.inet_aton(address)[::-1].hex().upper()


def tcp_line(
    *,
    local: str = "0.0.0.0",
    lport: int = 8080,
    remote: str = "0.0.0.0",
    rport: int = 0,
    state: str = "0A",
    uid: int = 1000,
    inode: int = 100,
) -> str:
    """Build one /proc/net/tcp row."""
    return (
        f"   0: {ipv4_hex(local)}:{lport:04X} {ipv4_hex(remote)}:{rport:04X} "
        f"{state} 00000000:00000000 00:00000000 00000000 {uid:5d} 0 {inode} "
        "1 0000000000000000 100 0 0 10 0"
    )


def unix_line(
    *, inode: int = 200, flags: int = 0x10000, path: str = "/run/x.sock"
) -> str:
    return f"0000000000000000: 00000002 00000000 {flags:08X} 0001 01 {inode} {path}"


def add_net(root: Path, *, tcp: list[str] = (), unix: list[str] = ()) -> None:
    net = root / "net"
    net.mkdir(parents=True, exist_ok=True)
    (net / "tcp").write_text(
        "  sl  local_address rem_address   st tx_queue rx_queue tr tm->when "
        "retrnsmt   uid  timeout inode\n" + "\n".join(tcp) + "\n"
    )
    (net / "unix").write_text(
        "Num RefCount Protocol Flags Type St Inode Path\n" + "\n".join(unix) + "\n"
    )


def write_proc(
    root: Path,
    pid: int,
    *,
    comm: str = "test",
    cmdline: str | None = None,
    uid: int = 1000,
    euid: int | None = None,
    ppid: int = 1,
    caps: int = 0,
    fds: tuple[tuple[str, str, bool], ...] = (),
    tty: bool = False,
    utime: int = 0,
    stime: int = 0,
    read_bytes: int = 4096,
    write_bytes: int = 8192,
    state: str = "S",
    threads: int = 2,
    rss_kb: int = 1024,
    starttime: int = 100,
    exe: str | None = None,
    io: bool = True,
    cgroup: str = "/user.slice/user-1000.slice/session-1.scope",
) -> Path:
    """Create a minimal but realistic /proc/<pid> tree."""
    d = root / str(pid)
    d.mkdir(parents=True, exist_ok=True)
    euid = uid if euid is None else euid
    (d / "stat").write_text(
        f"{pid} ({comm}) "
        + " ".join(
            [
                state,
                str(ppid),
                "0",
                "0",
                str(0x0101 if tty else 0),
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                str(utime),
                str(stime),
                "0",
                "0",
                "0",
                "0",
                str(threads),
                "0",
                str(starttime),
            ]
        )
        + "\n"
    )
    (d / "status").write_text(
        f"Name:\t{comm}\n"
        f"Uid:\t{uid}\t{euid}\t{uid}\t{uid}\n"
        f"VmRSS:\t{rss_kb:8d} kB\n"
        f"Threads:\t{threads}\n"
        f"CapEff:\t{caps:016x}\n"
        f"Seccomp:\t0\n"
        f"NoNewPrivs:\t0\n"
    )
    if cmdline is None:
        cmdline = f"{comm} --test"
    (d / "cmdline").write_text("\0".join(cmdline.split(" ")) + "\0", encoding="utf-8")
    exe = exe if exe is not None else f"/usr/bin/{comm}"
    exe_link = d / "exe"
    if exe_link.is_symlink() or exe_link.exists():
        exe_link.unlink()
    os.symlink(exe, exe_link)
    (d / "cgroup").write_text(f"0::/{cgroup.lstrip('/')}\n")
    if io:
        (d / "io").write_text(
            f"rchar: 10000\nwchar: 20000\nsyscr: 10\nsyscw: 20\n"
            f"read_bytes: {read_bytes}\nwrite_bytes: {write_bytes}\n"
            "cancelled_write_bytes: 0\n"
        )
    fd_dir = d / "fd"
    fd_dir.mkdir(exist_ok=True)
    for name, target, writable in fds:
        link = fd_dir / name
        if link.is_symlink() or link.exists():
            link.unlink()
        os.symlink(target, link)
        fd_dir.joinpath("..").joinpath("fdinfo").mkdir(exist_ok=True)
        (d / "fdinfo" / name).write_text(
            "pos:\t0\nflags:\t" + ("0100002" if writable else "0100000") + "\n"
        )
    return d


@pytest.fixture()
def proc_tree(tmp_path):
    root = tmp_path / "proc"
    root.mkdir()
    (root / "stat").write_text("cpu 1 2 3\nbtime 10000\n")
    return root


# ---------------------------------------------------------------------------
# XDG and config
# ---------------------------------------------------------------------------


def test_xdg_paths_use_environment(monkeypatch, tmp_path):
    for key in (
        "XDG_STATE_HOME",
        "XDG_CONFIG_HOME",
        "XDG_CACHE_HOME",
        "XDG_RUNTIME_DIR",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    paths = xdg_paths()
    assert paths.state == tmp_path / ".local" / "state"
    assert paths.config == tmp_path / ".config"
    assert paths.cache == tmp_path / ".cache"
    assert paths.runtime == paths.state
    assert paths.db == paths.state / "procwatch" / "baseline.db"
    assert paths.config_file == paths.config / "procwatch" / "config.toml"
    assert paths.lock == paths.state / "procwatch.lock"


def test_xdg_paths_honor_xdg_vars(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "run"))
    paths = xdg_paths()
    assert paths.state == tmp_path / "state"
    assert paths.runtime == tmp_path / "run"
    paths.ensure()
    assert (tmp_path / "state" / "procwatch").is_dir()
    assert (tmp_path / "config" / "procwatch").is_dir()
    assert (tmp_path / "cache" / "procwatch").is_dir()
    assert (tmp_path / "run").is_dir()


def test_config_defaults_and_load(tmp_path):
    assert Config().interval == 2.0
    path = tmp_path / "config.toml"
    path.write_text(
        "interval = 3.5\n"
        "write_rate_mb = 2\n"
        "read_rate_mb = 8\n"
        "rare_observations = 5\n"
        "cpu_percent = 40\n"
        'suspicious_paths = ["/tmp/", "/dev/shm/"]\n'
        "unknown_key = 1\n"
    )
    cfg = Config.load(path)
    assert cfg.interval == 3.5
    assert cfg.write_rate == 2 * 1024 * 1024
    assert cfg.read_rate == 8 * 1024 * 1024
    assert cfg.rare_observations == 5
    assert cfg.cpu_percent == 40
    assert cfg.suspicious_paths == ("/tmp/", "/dev/shm/")


def test_config_load_missing_returns_defaults(tmp_path):
    cfg = Config.load(tmp_path / "nope.toml")
    assert cfg == Config()


# ---------------------------------------------------------------------------
# formatting
# ---------------------------------------------------------------------------


def test_format_helpers():
    assert format_bytes(0) == "0B"
    assert format_bytes(999) == "999B"
    assert format_bytes(1024) == "1.0K"
    assert format_bytes(1536) == "1.5K"
    assert format_bytes(10 * 1024) == "10K"
    assert format_bytes(5 * 1024**3) == "5.0G"
    assert format_rate(1536) == "1.5K/s"
    assert format_age(9) == "9s"
    assert format_age(90) == "1m"
    assert format_age(3 * 3600) == "3h"
    assert format_age(2 * 86400) == "2d"
    assert truncate("abcdef", 4) == "abc…"
    assert truncate("abc", 4) == "abc"


# ---------------------------------------------------------------------------
# /proc parsing
# ---------------------------------------------------------------------------


def test_parse_proc_stat_handles_parens_and_fields():
    stat = "77 (evil) name) S 1 2 2 0 -1 4194560 1 0 0 0 12 34 0 0 20 0 3 0 987 0 0\n"
    parsed = parse_proc_stat(stat)
    assert parsed.comm == "evil) name"
    assert parsed.state == "S"
    assert parsed.ppid == 1
    assert parsed.utime == 12
    assert parsed.stime == 34
    assert parsed.threads == 3
    assert parsed.starttime == 987
    assert parsed.tty_nr == 0


def test_decode_inet_addr_v4_and_v6():
    assert decode_inet_addr("0100007F", 4) == ("127.0.0.1", 0)
    assert decode_inet_addr("0100007F:1F90", 4) == ("127.0.0.1", 8080)
    assert decode_inet_addr("00000000000000000000000001000000", 6) == ("::1", 0)
    assert decode_inet_addr("00000000000000000000000001000000:0050", 6) == ("::1", 80)


def test_parse_net_table_and_unix(proc_tree):
    text = (
        "header\n"
        + tcp_line(inode=100)
        + "\n"
        + tcp_line(
            local="127.0.0.1",
            lport=5555,
            remote="1.1.1.1",
            rport=443,
            state="01",
            inode=101,
        )
        + "\n"
    )
    table = parse_net_table(text, "tcp")
    assert table[100].listening is True
    assert table[100].local == ":8080"
    assert table[100].port == 8080
    assert table[101].listening is False
    assert table[101].remote == "1.1.1.1:443"
    assert table[101].state == "ESTAB"

    unix = parse_unix_table(
        "header\n"
        + unix_line(inode=200)
        + "\n"
        + unix_line(inode=201, flags=0, path="")
        + "\n"
    )
    assert unix[200].proto == "unix"
    assert unix[200].listening is True
    assert unix[200].local == "/run/x.sock"
    assert unix[201].listening is False


def test_capability_names_and_permission_score():
    assert capability_names(0) == frozenset()
    assert capability_names(1 << 12) == frozenset({"CAP_NET_ADMIN"})
    nobody = Process(pid=1, euid=1000)
    root = Process(pid=2, uid=0, euid=0)
    admin = Process(
        pid=3, uid=0, euid=0, caps=frozenset({"CAP_NET_ADMIN", "CAP_SYS_ADMIN"})
    )
    assert permission_score(root) > permission_score(nobody)
    assert permission_score(admin) > permission_score(root)


def test_procfs_snapshot_maps_sockets_and_io(proc_tree):
    add_net(
        proc_tree,
        tcp=[
            tcp_line(inode=100),
            tcp_line(
                local="127.0.0.1",
                lport=5555,
                remote="1.1.1.1",
                rport=443,
                state="01",
                inode=101,
            ),
        ],
        unix=[unix_line(inode=200)],
    )
    write_proc(
        proc_tree,
        100,
        comm="server",
        fds=(("3", "socket:[100]", False),),
        utime=250,
        stime=50,
    )
    write_proc(
        proc_tree,
        101,
        comm="client",
        caps=1 << 12,
        fds=(
            ("3", "socket:[101]", False),
            ("4", "socket:[200]", False),
            ("5", "/tmp/data", True),
        ),
        read_bytes=100,
        write_bytes=200,
    )
    snap = Procfs(proc_tree, use_ss=False).snapshot(now=100.0)
    assert [p.pid for p in snap.processes] == [100, 101]
    server, client = snap.processes
    assert len(server.listeners) == 1
    assert server.listeners[0].port == 8080
    assert server.cpu_seconds == pytest.approx(3.0)
    assert client.connections[0].remote == "1.1.1.1:443"
    assert len(client.unix_sockets) == 1
    assert client.open_files == 1
    assert client.open_writes == 1
    assert client.caps == frozenset({"CAP_NET_ADMIN"})
    assert client.tty is False
    assert client.fingerprint != server.fingerprint


def test_procfs_marks_unreadable_io(proc_tree):
    write_proc(proc_tree, 7, comm="secret", io=False)
    snap = Procfs(proc_tree, use_ss=False).snapshot(now=1.0)
    assert snap.processes[0].io_readable is False
    assert snap.processes[0].write_bytes == 0


def test_procfs_skips_processes_without_stat(proc_tree):
    (proc_tree / "999").mkdir()
    snap = Procfs(proc_tree, use_ss=False).snapshot(now=1.0)
    assert snap.processes == ()
    assert snap.errors


def test_parse_ss_tcp_info_sums_per_pid():
    text = """\
ESTAB 0 0 192.168.1.2%eth0:49001 1.1.1.1:443 users:(("curl",pid=1234,fd=5))
\t cubic bytes_sent:1000 bytes_received:2000 segs_out:4
ESTAB 0 0 192.168.1.2%eth0:49002 1.1.1.1:443 users:(("curl",pid=1234,fd=6))
\t cubic bytes_sent:500 bytes_received:100
ESTAB 0 0 192.168.1.2%eth0:49003 1.1.1.1:443 users:(("other",pid=99,fd=3))
\t cubic bytes_sent:7 bytes_received:0
"""
    assert parse_ss_tcp_info(text) == {1234: NetBytes(1500, 2100), 99: NetBytes(7, 0)}
    assert parse_ss_tcp_info("") == {}


# ---------------------------------------------------------------------------
# rates
# ---------------------------------------------------------------------------


def test_rate_tracker_computes_deltas(proc_tree):
    add_net(proc_tree)
    write_proc(
        proc_tree, 10, comm="worker", utime=100, read_bytes=1000, write_bytes=1000
    )
    tracker = procwatch.RateTracker()
    first = Procfs(proc_tree, use_ss=False).snapshot(now=100.0)
    rates = tracker.update(first)
    assert rates[10].cpu_percent == 0
    assert rates[10].write_rate == 0

    write_proc(
        proc_tree, 10, comm="worker", utime=300, read_bytes=5000, write_bytes=3048
    )
    second = Procfs(proc_tree, use_ss=False).snapshot(now=102.0)
    second = type(second)(
        ts=second.ts,
        processes=second.processes,
        net={10: NetBytes(4000, 500)},
        ss_available=True,
        errors=second.errors,
    )
    rates = tracker.update(second)
    assert rates[10].cpu_percent == pytest.approx(100.0)
    assert rates[10].read_rate == pytest.approx(2000.0)
    assert rates[10].write_rate == pytest.approx(1024.0)
    assert rates[10].tx_rate == pytest.approx(2000.0)
    assert rates[10].rx_rate == pytest.approx(250.0)


def test_rate_tracker_resets_on_pid_reuse(proc_tree):
    add_net(proc_tree)
    write_proc(proc_tree, 10, utime=100, starttime=100)
    tracker = procwatch.RateTracker()
    tracker.update(Procfs(proc_tree, use_ss=False).snapshot(now=1.0))
    write_proc(proc_tree, 10, utime=500, starttime=900)
    snap = Procfs(proc_tree, use_ss=False).snapshot(now=3.0)
    assert tracker.update(snap)[10].cpu_percent == 0


# ---------------------------------------------------------------------------
# baseline and novelty
# ---------------------------------------------------------------------------


def make_process(**overrides) -> Process:
    values = {
        "pid": 42,
        "ppid": 1,
        "uid": 1000,
        "euid": 1000,
        "comm": "demo",
        "cmdline": "demo --flag",
        "exe": "/usr/bin/demo",
        "state": "S",
        "threads": 4,
        "rss_bytes": 10 * 1024 * 1024,
        "cpu_seconds": 1.0,
        "starttime": 100,
        "started_at": 100.0,
        "read_bytes": 0,
        "write_bytes": 0,
        "open_files": 0,
        "open_writes": 0,
        "caps": frozenset(),
        "fingerprint": "fp-demo",
    }
    values.update(overrides)
    return Process(**values)


def make_profile(**overrides) -> Profile:
    values = {
        "fingerprint": "fp-demo",
        "exe": "/usr/bin/demo",
        "cmdline": "demo --flag",
        "comm": "demo",
        "uid": 1000,
        "first_seen": 0.0,
        "last_seen": 100.0,
        "observations": 10,
        "sockets_mean": 0.0,
        "sockets_m2": 0.0,
        "write_mean": 0.0,
        "write_m2": 0.0,
        "cpu_mean": 0.0,
        "cpu_m2": 0.0,
        "ports": frozenset(),
        "caps": frozenset(),
    }
    values.update(overrides)
    return Profile(**values)


def test_baseline_records_welford_stats(tmp_path):
    store = Baseline(tmp_path / "b.db", Config())
    p = make_process()
    store.record(
        [p], {42: Rates(write_rate=1000.0, cpu_percent=5.0)}, now=100.0, profiles={}
    )
    prof = store.profiles()["fp-demo"]
    assert prof.observations == 1
    assert prof.write_mean == 1000.0
    assert prof.cpu_mean == 5.0
    assert prof.first_seen == 100.0

    store.record([p], {42: Rates(write_rate=3000.0, cpu_percent=7.0)}, now=102.0)
    prof = store.profiles()["fp-demo"]
    assert prof.observations == 2
    assert prof.write_mean == pytest.approx(2000.0)
    assert prof.write_m2 == pytest.approx(2_000_000.0)
    assert prof.last_seen == 102.0
    store.close()


def test_novelty_new_rare_known_and_dormant():
    now = 1_000_000.0
    cfg = Config()
    p = make_process()
    new = assess_novelty(p, None, Rates(), now, cfg)
    assert new.level == "NEW"
    assert new.score >= 60
    assert "first seen" in " ".join(new.reasons)

    rare = assess_novelty(
        p, make_profile(observations=1, last_seen=now), Rates(), now, cfg
    )
    assert rare.level == "RARE"
    assert rare.score >= 30

    known = assess_novelty(p, make_profile(last_seen=now), Rates(), now, cfg)
    assert known == Novelty(0, "KNOWN", ())

    dormant = assess_novelty(
        p,
        make_profile(last_seen=now - 8 * 86400),
        Rates(),
        now,
        cfg,
    )
    assert dormant.level == "RETURNING"
    assert dormant.score >= 30


def test_novelty_flags_behavior_change_and_new_listener():
    now = 1_000_000.0
    p = make_process(
        sockets=(
            Socket(
                proto="tcp",
                inode=1,
                local=":9000",
                remote="",
                state="LISTEN",
                uid=1000,
                listening=True,
                port=9000,
            ),
        )
    )
    prof = make_profile(
        last_seen=now, ports=frozenset({80}), write_mean=1000.0, sockets_m2=0.0
    )
    nov = assess_novelty(p, prof, Rates(write_rate=100_000_000), now, Config())
    reasons = " | ".join(nov.reasons)
    assert nov.level == "CHANGED"
    assert "listener :9000" in reasons
    assert "write" in reasons
    assert nov.score > 40


def test_novelty_new_process_risk_markers():
    p = make_process(exe="/tmp/evil", euid=0, exe_deleted=True)
    nov = assess_novelty(p, None, Rates(), 100.0, Config())
    text = " ".join(nov.reasons)
    assert nov.level == "NEW"
    assert nov.score == 100
    assert "root" in text
    assert "/tmp" in text or "deleted" in text


def test_baseline_events_dedupe_and_reset(tmp_path):
    store = Baseline(tmp_path / "b.db", Config())
    assert store.record_event(
        100.0, "fp", 1, "x", "NEW", "first seen", dedupe_seconds=3600
    )
    assert not store.record_event(
        200.0, "fp", 1, "x", "NEW", "first seen", dedupe_seconds=3600
    )
    assert store.record_event(
        5000.0, "fp", 1, "x", "NEW", "first seen", dedupe_seconds=3600
    )
    events = store.recent_events()
    assert len(events) == 2
    assert events[0].ts == 5000.0
    store.record([make_process()], {42: Rates()}, now=1.0, profiles={})
    stats = store.stats()
    assert stats["identities"] == 1
    assert stats["events"] == 2
    store.reset()
    assert store.stats()["identities"] == 0
    assert store.recent_events() == []
    store.close()


# ---------------------------------------------------------------------------
# categorisation, sorting, filtering
# ---------------------------------------------------------------------------


def test_categorize_prefers_network_then_disk_then_cpu():
    cfg = Config()
    listener = make_process(
        pid=1,
        sockets=(Socket("tcp", 1, ":80", "", "LISTEN", 0, True, 80),),
    )
    client = make_process(
        pid=2,
        sockets=(Socket("tcp", 2, "127.0.0.1:5", "1.1.1.1:443", "ESTAB", 0, False, 5),),
    )
    writer = make_process(pid=3)
    shell = make_process(pid=4, tty_nr=0x0101)
    daemon = make_process(pid=5, ppid=1)
    kernel = make_process(pid=6, exe="", cmdline="")
    assert categorize(listener, Rates(), cfg) == "servers"
    assert categorize(client, Rates(), cfg) == "clients"
    assert categorize(writer, Rates(write_rate=2 * 1024**2), cfg) == "writers"
    assert categorize(writer, Rates(cpu_percent=50), cfg) == "compute"
    assert categorize(shell, Rates(), cfg) == "interactive"
    assert categorize(daemon, Rates(), cfg) == "daemons"
    assert categorize(kernel, Rates(), cfg) == "kernel"
    assert categorize(make_process(pid=7, ppid=999), Rates(), cfg) == "idle"


def test_build_rows_tags_and_metrics():
    cfg = Config(write_rate=1000, read_rate=2000, cpu_percent=10)
    p = make_process(
        sockets=(
            Socket("tcp", 1, ":80", "", "LISTEN", 1000, True, 80),
            Socket("tcp", 2, "127.0.0.1:5", "1.1.1.1:443", "ESTAB", 1000, False, 5),
            Socket("unix", 3, "/run/x.sock", "", "LISTEN", 1000, True),
        ),
        open_writes=3,
    )
    rows = build_rows(
        [p],
        {42: Rates(write_rate=5000, read_rate=5000, cpu_percent=20, tx_rate=100)},
        {42: Novelty(70, "NEW", ("x",))},
        cfg,
    )
    row = rows[0]
    assert row.conn_count == 2
    assert row.listen_count == 1
    assert row.remote_count == 1
    assert row.category == "servers"
    assert row.write_rate == 5000
    assert row.tx_rate == 100
    assert row.perm > 0
    assert set(row.tags) == {"LS", "NET", "WR", "RD", "CPU", "ROOT"} - {"ROOT"}


def test_sorting_and_filtering():
    cfg = Config()
    nov = Novelty(0, "KNOWN", ())
    a = build_rows([make_process(pid=1, comm="alpha")], {1: Rates()}, {1: nov}, cfg)[0]
    b = build_rows(
        [
            make_process(
                pid=2,
                comm="beta",
                sockets=(Socket("tcp", 1, ":1", "2.2.2.2:1", "ESTAB", 0),),
            )
        ],
        {2: Rates()},
        {2: nov},
        cfg,
    )[0]
    c = build_rows(
        [
            make_process(
                pid=3,
                comm="gamma",
                sockets=tuple(
                    Socket("tcp", i, f":{i}", "", "LISTEN", 0, True, i)
                    for i in range(3)
                ),
            )
        ],
        {3: Rates()},
        {3: nov},
        cfg,
    )[0]
    assert [
        r.process.pid for r in sort_rows([a, b, c], "connections", reverse=True)
    ] == [3, 2, 1]
    assert [r.process.pid for r in sort_rows([c, a, b], "name", reverse=False)] == [
        1,
        2,
        3,
    ]
    assert [r.process.pid for r in filter_rows([a, b, c], "bet")] == [2]
    assert [r.process.pid for r in filter_rows([a, b, c], "gamma")] == [3]


def test_group_rows_puts_novel_first_and_removes_duplicates():
    cfg = Config()
    rows = build_rows(
        [
            make_process(
                pid=1,
                comm="listener",
                sockets=(Socket("tcp", 1, ":80", "", "LISTEN", 0, True, 80),),
            ),
            make_process(pid=2, comm="brand-new"),
            make_process(pid=3, comm="old-timer", starttime=300, ppid=999),
        ],
        {1: Rates(), 2: Rates(), 3: Rates()},
        {
            1: Novelty(0, "KNOWN", ()),
            2: Novelty(70, "NEW", ("first seen",)),
            3: Novelty(30, "RARE", ("seen twice",)),
        },
        cfg,
    )
    groups = group_rows(rows, threshold=30)
    assert [name for name, _ in groups] == ["NEW & CHANGING", "NETWORK SERVERS"]
    assert [r.process.pid for _, rs in groups for r in rs] == [2, 3, 1]

    # Plain rare rows only float above the configured score threshold.
    groups = group_rows(rows, threshold=40)
    assert [name for name, _ in groups] == [
        "NEW & CHANGING",
        "NETWORK SERVERS",
        "IDLE",
    ]
    assert [r.process.pid for _, rs in groups for r in rs] == [2, 1, 3]


def test_kernel_worker_fingerprints_are_normalized():
    one = process_fingerprint("", "", "kworker/13:1-mm_percpu_wq", 0)
    two = process_fingerprint("", "", "kworker/u81:12+btrfs-endio", 0)
    other = process_fingerprint("", "", "ksoftirqd/0", 0)
    assert one == two
    assert one != other


# ---------------------------------------------------------------------------
# dashboard and CLI
# ---------------------------------------------------------------------------


def test_dashboard_renders_main_and_all_views(proc_tree, tmp_path):
    add_net(
        proc_tree,
        tcp=[
            tcp_line(inode=100),
            tcp_line(
                local="127.0.0.1",
                lport=5555,
                remote="1.1.1.1",
                rport=443,
                state="01",
                inode=101,
            ),
        ],
    )
    write_proc(proc_tree, 100, comm="server", fds=(("3", "socket:[100]", False),))
    write_proc(
        proc_tree,
        101,
        comm="client",
        fds=(("3", "socket:[101]", False),),
        write_bytes=0,
    )
    write_proc(proc_tree, 102, comm="writer", ppid=1, write_bytes=0)

    cfg = Config(interval=1, rare_observations=1, write_rate=1000, cpu_percent=90)
    store = Baseline(tmp_path / "b.db", cfg)
    dash = Dashboard(Procfs(proc_tree, use_ss=False), store, cfg)
    dash.poll(now=1000.0)
    write_proc(proc_tree, 102, comm="writer", ppid=1, write_bytes=5000)
    dash.poll(now=1001.0)

    main_text = "\n".join(line.text for line in dash.render(140, 40))
    assert "procwatch" in main_text
    assert "NETWORK SERVERS" in main_text
    assert "NETWORK CLIENTS" in main_text
    assert "DISK WRITERS" in main_text
    assert "LS" in main_text

    dash.set_view("all")
    dash.sort_by("connections")
    all_text = "\n".join(line.text for line in dash.render(140, 40))
    assert "All processes" in all_text
    assert all_text.index("server") < all_text.index("writer")

    dash.sort_by("write")
    all_text = "\n".join(line.text for line in dash.render(140, 40))
    assert all_text.index("writer") < all_text.index("server")

    dash.set_filter("client")
    filtered = "\n".join(line.text for line in dash.render(140, 40))
    assert "client" in filtered
    assert "server" not in filtered
    store.close()


def test_dashboard_new_process_floats_to_top(proc_tree, tmp_path):
    add_net(proc_tree, tcp=[tcp_line(inode=100)])
    write_proc(proc_tree, 100, comm="server", fds=(("3", "socket:[100]", False),))
    cfg = Config(rare_observations=1)
    store = Baseline(tmp_path / "b.db", cfg)
    dash = Dashboard(Procfs(proc_tree, use_ss=False), store, cfg)
    dash.poll(now=100.0)
    write_proc(proc_tree, 200, comm="intruder", exe="/tmp/intruder", euid=0)
    dash.poll(now=101.0)
    text = "\n".join(line.text for line in dash.render(140, 40))
    assert text.index("intruder") < text.index("server")
    assert "NEW & CHANGING" in text
    store.close()


def test_dashboard_filter_input(proc_tree, tmp_path):
    add_net(proc_tree)
    write_proc(proc_tree, 1, comm="alpha")
    write_proc(proc_tree, 2, comm="beta")
    cfg = Config()
    store = Baseline(tmp_path / "b.db", cfg)
    dash = Dashboard(Procfs(proc_tree, use_ss=False), store, cfg)
    dash.poll(now=1.0)
    dash.begin_filter()
    for ch in map(ord, "bet"):
        dash.handle_filter_key(ch)
    dash.handle_filter_key(10)
    assert dash.filter_text == "bet"
    assert [r.process.comm for r in dash.visible_rows()] == ["beta"]
    store.close()


def test_cli_snapshot_json(proc_tree, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "run"))
    add_net(proc_tree, tcp=[tcp_line(inode=100)])
    write_proc(proc_tree, 100, comm="server", fds=(("3", "socket:[100]", False),))
    db = tmp_path / "b.db"
    rc = procwatch.main(
        [
            "--snapshot",
            "--json",
            "--db",
            str(db),
            "--proc-root",
            str(proc_tree),
            "--limit",
            "10",
        ]
    )
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["processes"][0]["pid"] == 100
    assert data["processes"][0]["category"] == "servers"
    assert data["processes"][0]["listening"] == 1
    assert data["baseline"]["identities"] == 1

    rc = procwatch.main(["--baseline", "--db", str(db)])
    assert rc == 0
    assert "identities: 1" in capsys.readouterr().out


def test_cli_snapshot_text_and_no_record(proc_tree, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "run"))
    add_net(proc_tree)
    write_proc(proc_tree, 1, comm="alpha")
    db = tmp_path / "b.db"
    rc = procwatch.main(
        ["--snapshot", "--db", str(db), "--proc-root", str(proc_tree), "--no-record"]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "NEW & CHANGING" in out
    assert Baseline(db, Config()).stats()["identities"] == 0


def test_textual_app_smoke(proc_tree, tmp_path):
    if not procwatch.TEXTUAL_AVAILABLE:
        pytest.skip("modern textual is available only under uv in this environment")

    add_net(
        proc_tree,
        tcp=[
            tcp_line(inode=100),
            tcp_line(
                local="127.0.0.1",
                lport=5555,
                remote="1.1.1.1",
                rport=443,
                state="01",
                inode=101,
            ),
        ],
    )
    write_proc(proc_tree, 100, comm="server", fds=(("3", "socket:[100]", False),))
    write_proc(
        proc_tree,
        101,
        comm="client",
        fds=(("3", "socket:[101]", False),),
        write_bytes=0,
    )
    write_proc(proc_tree, 102, comm="writer", ppid=1, write_bytes=0)

    cfg = Config(interval=999, rare_observations=1, write_rate=1000)
    store = Baseline(tmp_path / "b.db", cfg)
    dash = Dashboard(Procfs(proc_tree, use_ss=False), store, cfg)
    dash.poll(now=1000.0)
    write_proc(proc_tree, 102, comm="writer", ppid=1, write_bytes=5000)
    dash.poll(now=1001.0)

    app = procwatch.ProcWatchApp(dash, auto_poll=False)

    async def scenario() -> None:
        async with app.run_test(size=(140, 45)) as pilot:
            await pilot.pause()
            main = app.query_one("#table-main", procwatch.DataTable)
            assert main.row_count == 3
            assert dash.view == "main"
            assert app.selected_keys.get("table-main")
            await pilot.press("2")
            await pilot.pause()
            assert dash.view == "all"
            all_table = app.query_one("#table-all", procwatch.DataTable)
            assert all_table.row_count == 3
            await pilot.press("s")
            await pilot.pause()
            assert dash.sort_key != "connections"

    asyncio.run(scenario())
    store.close()


def test_textual_help_and_manual_refresh(proc_tree, tmp_path):
    if not procwatch.TEXTUAL_AVAILABLE:
        pytest.skip("modern textual is available only under uv in this environment")

    write_proc(proc_tree, 100, comm="server")
    write_proc(proc_tree, 101, comm="client")

    cfg = Config(interval=999)
    store = Baseline(tmp_path / "b.db", cfg)
    dash = Dashboard(Procfs(proc_tree, use_ss=False), store, cfg)
    dash.poll(now=1000.0)
    first_sample = dash.snapshot_ts

    app = procwatch.ProcWatchApp(dash)

    async def scenario() -> None:
        async with app.run_test(size=(100, 20)) as pilot:
            await pilot.pause()
            assert app.auto_poll is False
            assert app.refresh_timer is None

            await pilot.press("r")
            await pilot.pause()
            assert dash.snapshot_ts != first_sample

            await pilot.press("R")
            await pilot.pause()
            assert app.auto_poll is True
            assert app.refresh_timer is not None

            await pilot.press("R")
            await pilot.pause()
            assert app.auto_poll is False
            assert app.refresh_timer is None

            await pilot.press("question_mark")
            await pilot.pause()
            assert isinstance(app.screen, procwatch.HelpScreen)

            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, procwatch.HelpScreen)

            await pilot.press("question_mark")
            await pilot.pause()
            assert isinstance(app.screen, procwatch.HelpScreen)

            await pilot.press("q")
            await pilot.pause()
            assert not isinstance(app.screen, procwatch.HelpScreen)
            assert app.is_running

    asyncio.run(scenario())
    store.close()


def test_textual_refresh_keeps_scrollbar(proc_tree, tmp_path):
    if not procwatch.TEXTUAL_AVAILABLE:
        pytest.skip("modern textual is available only under uv in this environment")

    for pid in range(100, 140):
        write_proc(proc_tree, pid, comm=f"p{pid}")

    cfg = Config(interval=999)
    store = Baseline(tmp_path / "b.db", cfg)
    dash = Dashboard(Procfs(proc_tree, use_ss=False), store, cfg)
    dash.poll(now=1000.0)

    app = procwatch.ProcWatchApp(dash)

    async def scenario() -> None:
        async with app.run_test(size=(100, 20)) as pilot:
            await pilot.pause()
            await pilot.press("2")
            await pilot.pause()
            table = app.query_one("#table-all", procwatch.DataTable)
            assert table.row_count == 40
            table.scroll_to(y=10, animate=False)
            await pilot.pause()
            assert table.scroll_y == 10

            app.refresh_views()
            await pilot.pause()
            assert table.scroll_y == 10

    asyncio.run(scenario())
    store.close()


def test_aggregate_views_and_risk(proc_tree, tmp_path):
    add_net(
        proc_tree,
        tcp=[
            tcp_line(inode=100),
            tcp_line(
                local="127.0.0.1",
                lport=5555,
                remote="1.1.1.1",
                rport=443,
                state="01",
                inode=101,
            ),
        ],
    )
    write_proc(
        proc_tree,
        100,
        comm="nginx",
        ppid=1,
        fds=(("3", "socket:[100]", False),),
    )
    write_proc(
        proc_tree,
        101,
        comm="nginx",
        ppid=1,
        fds=(("3", "socket:[101]", False),),
        cgroup="/docker/web",
    )
    write_proc(proc_tree, 102, comm="rootproc", uid=0, euid=0)
    write_proc(proc_tree, 103, comm="capproc", caps=1 << 21)

    cfg = Config(interval=999)
    store = Baseline(tmp_path / "b.db", cfg)
    dash = Dashboard(Procfs(proc_tree, use_ss=False), store, cfg)
    dash.poll(now=1000.0)

    dash.set_view("commands")
    command = next(
        row
        for row in dash.visible_items()
        if isinstance(row, procwatch.CommandRow) and row.comm == "nginx"
    )
    assert command.count == 2
    assert command.conn_count == 2
    assert command.pids == (100, 101)
    assert "2 process(es)" in dash.detail_lines(command)[0][0]

    dash.set_view("cgroups")
    cgroups = {row.path: row for row in dash.visible_items()}
    assert cgroups["/docker/web"].count == 1
    assert cgroups["/user.slice/user-1000.slice/session-1.scope"].count == 3

    dash.set_view("network")
    endpoints = dash.visible_items()
    exposures = {endpoint.exposure for endpoint in endpoints}
    assert exposures == {"PUBLIC", "REMOTE"}
    assert endpoints[0].exposure == "PUBLIC"
    assert dash.detail_lines(endpoints[0])[0][1] == "bold"

    dash.set_view("risk")
    risk_pids = {row.process.pid for row in dash.visible_items()}
    assert risk_pids == {102, 103}
    assert any("caps" in line for line, _ in dash.detail_lines(dash.visible_items()[0]))

    store.close()


def test_tree_age_sort_and_novelty_filter(proc_tree, tmp_path):
    write_proc(proc_tree, 1, comm="init", starttime=100)
    write_proc(proc_tree, 10, comm="parent", ppid=1, starttime=200)
    write_proc(proc_tree, 11, comm="child", ppid=10, starttime=300)
    write_proc(proc_tree, 12, comm="child2", ppid=10, starttime=400)

    cfg = Config(interval=999, rare_observations=1, warm_identities=0)
    store = Baseline(tmp_path / "b.db", cfg)
    dash = Dashboard(Procfs(proc_tree, use_ss=False), store, cfg)
    dash.poll(now=1000.0)
    dash.poll(now=1001.0)

    dash.set_view("all")
    dash.set_sort("age")
    assert [row.process.pid for row in dash.visible_rows()] == [12, 11, 10, 1]

    dash.toggle_tree()
    rows = dash.visible_rows()
    assert [row.process.pid for row in rows] == [1, 10, 11, 12]
    parent = next(row for row in rows if row.process.pid == 10)
    assert dash.display_command(parent).startswith("  ")
    assert any(text.startswith("baseline:") for text, _ in dash.detail_lines(rows[0]))

    dash.cycle_novelty_filter()
    assert dash.novelty_filter == "NEW"
    assert dash.visible_rows() == []
    dash.cycle_novelty_filter(-1)
    assert dash.novelty_filter == ""
    assert len(dash.visible_rows()) == 4

    store.close()


def test_textual_views_and_shortcuts(proc_tree, tmp_path):
    if not procwatch.TEXTUAL_AVAILABLE:
        pytest.skip("modern textual is available only under uv in this environment")

    add_net(proc_tree, tcp=[tcp_line(inode=100)])
    write_proc(proc_tree, 1, comm="init")
    write_proc(proc_tree, 100, comm="server", fds=(("3", "socket:[100]", False),))
    write_proc(proc_tree, 101, comm="rootproc", uid=0, euid=0)
    write_proc(proc_tree, 102, comm="child", ppid=100)

    cfg = Config(interval=2.0, rare_observations=1, warm_identities=0)
    store = Baseline(tmp_path / "b.db", cfg)
    dash = Dashboard(Procfs(proc_tree, use_ss=False), store, cfg)
    dash.poll(now=1000.0)
    dash.poll(now=1001.0)

    app = procwatch.ProcWatchApp(dash)

    async def scenario() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()

            for key, view, table_id in (
                ("4", "commands", "table-commands"),
                ("5", "network", "table-network"),
                ("6", "cgroups", "table-cgroups"),
                ("7", "risk", "table-risk"),
            ):
                await pilot.press(key)
                await pilot.pause()
                assert dash.view == view
                assert app.query_one(f"#{table_id}", procwatch.DataTable).row_count

            await pilot.press("exclamation_mark")
            await pilot.pause()
            assert dash.view == "risk"

            await pilot.press("2")
            await pilot.pause()
            await pilot.press("t")
            await pilot.pause()
            assert dash.tree_mode
            await pilot.press("n")
            await pilot.pause()
            assert dash.novelty_filter == "NEW"
            await pilot.press("c")
            await pilot.pause()
            assert dash.novelty_filter == ""

            await pilot.press("w")
            await pilot.pause()
            assert app.compact
            assert len(app.query_one("#table-all", procwatch.DataTable).columns) == 5
            await pilot.press("w")
            await pilot.pause()
            assert not app.compact

            await pilot.press("1")
            await pilot.pause()
            first_group = app.selected_groups.get("table-main")
            await pilot.press("right_square_bracket")
            await pilot.pause()
            assert app.selected_groups.get("table-main") != first_group
            await pilot.press("left_square_bracket")
            await pilot.pause()
            assert app.selected_groups.get("table-main") == first_group

            await pilot.press("enter")
            await pilot.pause()
            assert isinstance(app.screen, procwatch.DetailScreen)
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, procwatch.DetailScreen)

            interval = dash.config.interval
            await pilot.press("plus")
            await pilot.pause()
            assert dash.config.interval > interval
            await pilot.press("minus")
            await pilot.pause()
            assert dash.config.interval == interval

            await pilot.press("y")
            await pilot.pause()
            assert app.clipboard

    asyncio.run(scenario())
    store.close()
