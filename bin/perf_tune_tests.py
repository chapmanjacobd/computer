#!/usr/bin/env python3
"""Tests for perf.tune."""

from __future__ import annotations

import dataclasses
import doctest
import json
import runpy
import types
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).with_name("perf.tune")
MODULE = types.ModuleType("perf_tune")
MODULE.__dict__.update(runpy.run_path(str(MODULE_PATH)))
lt = MODULE


@pytest.fixture
def snapshot():
    """Build a Snapshot with only the fields a test cares about."""

    def make(**overrides: object) -> object:
        return lt.Snapshot(**overrides)

    return make


def test_doctests() -> None:
    results = doctest.testmod(MODULE, verbose=False)
    assert results.failed == 0


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("always [madvise] never", "madvise"),
        ("none", "none"),
        ("", ""),
    ],
)
def test_bracket_value(text: str, expected: str) -> None:
    assert lt.bracket_value(text) == expected


def test_parse_psi() -> None:
    parsed = lt.parse_psi("some avg10=12.50 avg60=3.00 avg300=1.00 total=42\nfull avg10=0.00 total=0\n")
    assert parsed["some"]["avg10"] == pytest.approx(12.5)
    assert parsed["full"]["avg10"] == pytest.approx(0.0)


def test_parse_meminfo() -> None:
    parsed = lt.parse_meminfo("MemTotal:       32768 kB\nMemAvailable:    8192 kB\n")
    assert parsed == {"MemTotal": 32768, "MemAvailable": 8192}


def test_parse_interrupts() -> None:
    text = " 126: 1 2 3 4 xhci_hcd\n 134: 5 6 7 8 IR-PCI nvme0q1\n LOC: 9 9 9 9\n"
    assert lt.parse_interrupts(text) == {"xhci_hcd": 10, "nvme0q1": 26}


def test_diff_counters() -> None:
    before = lt.Counters(
        timestamp=10.0,
        cpu_total=1000,
        cpu_idle=500,
        ctxt=100,
        disks={"nvme0n1": (10, 100, 20, 200)},
        net_rx=0,
        net_tx=0,
        irqs={"xhci_hcd": 100},
    )
    after = lt.Counters(
        timestamp=11.0,
        cpu_total=2000,
        cpu_idle=600,
        ctxt=1100,
        disks={"nvme0n1": (30, 300, 40, 600)},
        net_rx=1_048_576,
        net_tx=2_097_152,
        irqs={"xhci_hcd": 300},
    )
    sample = lt.diff_counters(before, after)
    assert sample.seconds == pytest.approx(1.0)
    assert sample.cpu_busy_pct == pytest.approx(90.0)
    assert sample.ctxt_per_s == pytest.approx(1000.0)
    assert sample.disk_read_mib_s == pytest.approx(200 * 512 / 1048576)
    assert sample.disk_write_mib_s == pytest.approx(400 * 512 / 1048576)
    assert sample.iops == pytest.approx(40.0)
    assert sample.net_rx_mib_s == pytest.approx(1.0)
    assert sample.net_tx_mib_s == pytest.approx(2.0)
    assert sample.irq_rates == (("xhci_hcd", pytest.approx(200.0)),)


def test_evaluate_load_flags_saturation(snapshot) -> None:
    findings = lt.evaluate_load(snapshot(ncpu=4, load1=12.0, cpu_busy_pct=99.0, psi_cpu_some=65.0))
    by_key = {finding.key: finding for finding in findings}
    assert by_key["cpu-saturated"].status == "crit"
    assert "CPU is saturated" in by_key["cpu-saturated"].title


def test_evaluate_load_quiet_when_idle(snapshot) -> None:
    findings = lt.evaluate_load(snapshot(ncpu=8, load1=0.2, cpu_busy_pct=4.0, psi_cpu_some=0.0))
    by_key = {finding.key: finding for finding in findings}
    assert by_key["cpu-busy"].status == "ok"


def test_evaluate_memory_flags_oom(snapshot) -> None:
    findings = lt.evaluate_memory(
        snapshot(
            mem_total_kib=32 * 1024 * 1024,
            mem_available_kib=1024 * 1024,
            swap_total_kib=16 * 1024 * 1024,
            swap_free_kib=1024,
            psi_mem_some=30.0,
            psi_mem_full=8.0,
            oom_count=2,
            oom_victims=("ffmpeg", "ffmpeg"),
        )
    )
    finding = findings[0]
    assert finding.key == "memory-pressure"
    assert finding.status == "crit"
    assert "ffmpeg" in finding.detail


def test_usb_auto_creates_runtime_and_udev(snapshot) -> None:
    device = lt.UsbInput(
        name="USB Receiver",
        vendor="046d",
        product="c52b",
        control="auto",
        delay_ms=2000,
        sysfs="/sys/bus/usb/devices/1-4.3",
    )
    findings = lt.evaluate_usb(snapshot(usb_inputs=(device,)))
    by_key = {finding.key: finding for finding in findings}
    finding = by_key["usb-input-power"]
    assert finding.status == "warn"
    assert finding.writes == (lt.Write("/sys/bus/usb/devices/1-4.3/power/control", "on"),)
    assert any('ATTR{idVendor}=="046d"' in rule for rule in finding.udev)


def test_usb_reconnect_is_warning(snapshot) -> None:
    findings = lt.evaluate_usb(snapshot(usb_inputs=(), usb_reconnects=(("Compx 2.4G Receiver Mouse", 3),)))
    by_key = {finding.key: finding for finding in findings}
    assert by_key["usb-reconnect"].status == "warn"
    assert "x3" in by_key["usb-reconnect"].detail


def test_epp_tune_writes_each_cpu(snapshot) -> None:
    findings = lt.evaluate_cpu(
        snapshot(
            intel_pstate=True,
            governors=(("powersave", 2),),
            epps=((0, "power"), (1, "balance_power")),
        )
    )
    by_key = {finding.key: finding for finding in findings}
    finding = by_key["cpu-epp"]
    assert finding.apply_by_default is True
    paths = {write.path for write in finding.writes}
    assert "/sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference" in paths
    assert "/sys/devices/system/cpu/cpu1/cpufreq/energy_performance_preference" in paths
    assert finding.service


def test_deep_cstate_is_aggressive(snapshot) -> None:
    states = (
        lt.CpuIdleState(index=0, name="POLL", latency_us=0, disabled=False),
        lt.CpuIdleState(index=3, name="C3_ACPI", latency_us=1048, disabled=False),
    )
    findings = lt.evaluate_cpu(snapshot(ncpu=2, cpuidle=states))
    by_key = {finding.key: finding for finding in findings}
    assert by_key["cpu-cstates"].apply_by_default is False
    assert len(by_key["cpu-cstates"].writes) == 2


def test_ssd_scheduler_suggests_none(snapshot) -> None:
    devices = (
        lt.BlockDevice(name="nvme0n1", rotational=False, scheduler="mq-deadline"),
        lt.BlockDevice(name="sda", rotational=True, scheduler="bfq"),
    )
    findings = lt.evaluate_storage(snapshot(block_devices=devices))
    by_key = {finding.key: finding for finding in findings}
    finding = by_key["block-scheduler-ssd"]
    assert finding.writes == (lt.Write("/sys/block/nvme0n1/queue/scheduler", "none"),)
    assert finding.apply_by_default is True


def test_hdd_scheduler_is_aggressive(snapshot) -> None:
    devices = (lt.BlockDevice(name="sda", rotational=True, scheduler="mq-deadline"),)
    findings = lt.evaluate_storage(snapshot(block_devices=devices))
    by_key = {finding.key: finding for finding in findings}
    assert by_key["block-scheduler-hdd"].apply_by_default is False


def test_selected_findings_respects_aggressive(snapshot) -> None:
    findings = lt.evaluate_cpu(
        snapshot(
            intel_pstate=True,
            governors=(("powersave", 1),),
            epps=((0, "power"),),
            cpuidle=(lt.CpuIdleState(index=3, name="C3", latency_us=5000, disabled=False),),
        )
    )
    safe_keys = {finding.key for finding in lt.selected_findings(findings, aggressive=False)}
    all_keys = {finding.key for finding in lt.selected_findings(findings, aggressive=True)}
    assert "cpu-epp" in safe_keys
    assert "cpu-cstates" not in safe_keys
    assert "cpu-cstates" in all_keys


def test_balanced_skips_cstates_and_hdd_bfq(snapshot) -> None:
    states = (lt.CpuIdleState(index=3, name="C3", latency_us=5000, disabled=False),)
    cpu_findings = lt.evaluate_cpu(snapshot(ncpu=2, cpuidle=states), "balanced")
    assert "cpu-cstates" not in {finding.key for finding in cpu_findings}

    devices = (lt.BlockDevice(name="sda", rotational=True, scheduler="mq-deadline"),)
    storage_findings = lt.evaluate_storage(snapshot(block_devices=devices), "balanced")
    assert "block-scheduler-hdd" not in {finding.key for finding in storage_findings}


def test_latency_hdd_targets_bfq(snapshot) -> None:
    devices = (lt.BlockDevice(name="sda", rotational=True, scheduler="mq-deadline"),)
    findings = lt.evaluate_storage(snapshot(block_devices=devices), "latency")
    finding = {entry.key: entry for entry in findings}["block-scheduler-hdd"]
    assert finding.target == "bfq"
    assert finding.apply_by_default is False
    assert finding.writes == (lt.Write("/sys/block/sda/queue/scheduler", "bfq"),)


def test_throughput_hdd_targets_mq_deadline(snapshot) -> None:
    devices = (lt.BlockDevice(name="sda", rotational=True, scheduler="bfq"),)
    findings = lt.evaluate_storage(snapshot(block_devices=devices), "throughput")
    finding = {entry.key: entry for entry in findings}["block-scheduler-hdd"]
    assert finding.target == "mq-deadline"
    assert finding.apply_by_default is True
    assert finding.writes == (lt.Write("/sys/block/sda/queue/scheduler", "mq-deadline"),)
    assert 'ATTR{queue/scheduler}="mq-deadline"' in finding.udev[0]


def test_throughput_epp_and_governor_target_performance(snapshot) -> None:
    data = snapshot(
        ncpu=2,
        intel_pstate=True,
        governors=(("powersave", 2),),
        epps=((0, "balance_performance"), (1, "balance_performance")),
    )
    findings = lt.evaluate_cpu(data, "throughput")
    by_key = {finding.key: finding for finding in findings}
    assert by_key["cpu-epp"].target == "performance"
    assert all(write.value == "performance" for write in by_key["cpu-epp"].writes)
    assert by_key["cpu-governor"].target == "performance"
    assert len(by_key["cpu-governor"].writes) == 2


def test_throughput_skips_latency_only_tweaks(snapshot) -> None:
    data = snapshot(
        ncpu=2,
        dirty_bytes=2 * 1024**3,
        zram_disksize=16 * 1024**3,
        page_cluster=3,
        thp="always",
        cpuidle=(lt.CpuIdleState(index=3, name="C3", latency_us=5000, disabled=False),),
    )
    storage = lt.evaluate_storage(data, "throughput")
    storage_keys = {finding.key for finding in storage}
    assert "dirty-writeback" not in storage_keys
    assert "zram-page-cluster" not in storage_keys
    assert "thp" not in storage_keys

    cpu = lt.evaluate_cpu(data, "throughput")
    assert "cpu-cstates" not in {finding.key for finding in cpu}


def test_throughput_readahead(snapshot) -> None:
    devices = (lt.BlockDevice(name="sda", rotational=True, scheduler="mq-deadline", read_ahead_kb=1024),)
    findings = lt.evaluate_storage(snapshot(block_devices=devices), "throughput")
    finding = {entry.key: entry for entry in findings}["block-readahead"]
    assert finding.target == "4096 KiB"
    assert finding.writes == (lt.Write("/sys/block/sda/queue/read_ahead_kb", "4096"),)


def test_format_report_shows_profile(snapshot) -> None:
    report = lt.format_report(snapshot(host="test"), [], "throughput")
    assert "profile  throughput" in report


def test_report_dict_includes_profile(snapshot) -> None:
    payload = lt.report_as_dict(snapshot(), [], profile="balanced")
    assert payload["profile"] == "balanced"


def test_parse_args_profile() -> None:
    args = lt.parse_args(["--profile", "throughput"])
    assert args.profile == "throughput"


def test_collect_cpuidle_parses_state_index(tmp_path: Path) -> None:
    state = tmp_path / "devices" / "system" / "cpu" / "cpu0" / "cpuidle" / "state3"
    state.mkdir(parents=True)
    (state / "name").write_text("C3\n")
    (state / "latency").write_text("1048\n")
    (state / "disable").write_text("0\n")

    assert lt.collect_cpuidle(tmp_path) == (
        lt.CpuIdleState(index=3, name="C3", latency_us=1048, disabled=False),
    )


def test_tuned_verify_failure_is_a_warning(snapshot) -> None:
    findings = lt.evaluate_general(snapshot(tuned_profile="throughput-performance", tuned_verified=False))
    by_key = {finding.key: finding for finding in findings}
    assert by_key["tuned-profile"].status == "warn"
    assert "verification failed" in by_key["tuned-profile"].current


def test_build_sysctl_conf() -> None:
    findings = [
        lt.Finding(
            key="x",
            title="x",
            status="info",
            detail="x",
            sysctl=(("vm.page-cluster", "0"),),
        )
    ]
    content = lt.build_sysctl_conf(findings)
    assert lt.MANAGED_MARKER in content
    assert "vm.page-cluster = 0" in content


def test_build_service_unit() -> None:
    findings = [
        lt.Finding(
            key="x",
            title="x",
            status="info",
            detail="x",
            service=("echo 1 > /sys/example",),
        )
    ]
    content = lt.build_service_unit(findings)
    assert "ExecStart=/bin/sh -c 'echo 1 > /sys/example'" in content
    assert "WantedBy=multi-user.target" in content


def test_write_managed_refuses_foreign_file(tmp_path: Path) -> None:
    path = tmp_path / "conf"
    path.write_text("hand written\n")
    with pytest.raises(ValueError):
        lt.write_managed(path, f"# {lt.MANAGED_MARKER}\nnew\n")


def test_write_managed_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "conf"
    content = f"# {lt.MANAGED_MARKER}\nvalue = 1\n"
    assert lt.write_managed(path, content) == "wrote"
    assert lt.write_managed(path, content) == "unchanged"


def test_apply_runtime_writes_when_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "value"
    target.write_text("old\n")
    monkeypatch.setattr(lt.os, "geteuid", lambda: 0)
    results = lt.apply_runtime([lt.Write(str(target), "42")], execute=True)
    assert results[0].action == "applied"
    assert target.read_text() == "42\n"


def test_apply_runtime_reports_permission_without_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "value"
    target.write_text("old\n")
    monkeypatch.setattr(lt.os, "geteuid", lambda: 1000)
    results = lt.apply_runtime([lt.Write(str(target), "42")], execute=True)
    assert results[0].action == "denied"
    assert target.read_text() == "old\n"


def test_apply_permanent_removes_stale_managed_file(tmp_path: Path) -> None:
    path = tmp_path / "sysctl.d" / lt.SYSCTL_CONF
    lt.write_managed(path, f"# {lt.MANAGED_MARKER}\nvm.page-cluster = 0\n")
    assert path.exists()
    lt.apply_permanent([], tmp_path)
    assert not path.exists()


def test_apply_permanent_links_service_unit(tmp_path: Path) -> None:
    findings = [
        lt.Finding(
            key="x",
            title="x",
            status="info",
            detail="x",
            service=("echo 1 > /sys/example",),
        )
    ]
    lt.apply_permanent(findings, tmp_path)
    wants = tmp_path / "systemd" / "system" / "multi-user.target.wants" / lt.SERVICE_UNIT
    assert wants.is_symlink()


def test_plan_permanent_create_update_and_diff(tmp_path: Path) -> None:
    finding = lt.Finding(
        key="x",
        title="x",
        status="info",
        detail="x",
        sysctl=(("vm.page-cluster", "0"),),
    )
    path = tmp_path / "sysctl.d" / lt.SYSCTL_CONF

    plan = lt.plan_permanent([finding], tmp_path)
    item = {entry.path: entry for entry in plan}[path]
    assert item.action == "create"
    assert "--- /dev/null" in item.diff
    assert "+vm.page-cluster = 0" in item.diff

    lt.apply_plan(plan, tmp_path)
    assert path.exists()

    unchanged = {entry.path: entry for entry in lt.plan_permanent([finding], tmp_path)}[path]
    assert unchanged.action == "unchanged"

    finding2 = dataclasses.replace(
        finding,
        sysctl=(("vm.page-cluster", "0"), ("fs.inotify.max_user_watches", "524288")),
    )
    update = {entry.path: entry for entry in lt.plan_permanent([finding2], tmp_path)}[path]
    assert update.action == "update"
    assert "-vm.page-cluster = 0" not in update.diff
    assert "+fs.inotify.max_user_watches = 524288" in update.diff


def test_plan_permanent_conflict_is_not_written(tmp_path: Path) -> None:
    path = tmp_path / "sysctl.d" / lt.SYSCTL_CONF
    path.parent.mkdir(parents=True)
    path.write_text("hand written\n")
    finding = lt.Finding(
        key="x",
        title="x",
        status="info",
        detail="x",
        sysctl=(("vm.page-cluster", "0"),),
    )

    plan = lt.plan_permanent([finding], tmp_path)
    item = {entry.path: entry for entry in plan}[path]
    assert item.action == "conflict"
    assert "-hand written" in item.diff

    results = lt.apply_plan(plan, tmp_path)
    assert (path, "conflict") in results
    assert path.read_text() == "hand written\n"


def test_format_permanent_plan_includes_diff(tmp_path: Path) -> None:
    finding = lt.Finding(
        key="x",
        title="x",
        status="info",
        detail="x",
        sysctl=(("vm.page-cluster", "0"),),
    )
    plan = lt.plan_permanent([finding], tmp_path)
    text = lt.format_permanent_plan(plan)
    assert f"+ {tmp_path / 'sysctl.d' / lt.SYSCTL_CONF}" in text
    assert "--- /dev/null" in text
    assert "+++ " in text
    assert "1 create" in text


def test_scan_rpm_conflicts(tmp_path: Path) -> None:
    base = tmp_path / "sysctl.d" / "99-example.conf"
    base.parent.mkdir(parents=True)
    base.write_text("old = 1\n")
    sibling = base.with_name(base.name + ".rpmnew")
    sibling.write_text("old = 2\n")

    conflicts = lt.scan_rpm_conflicts(tmp_path)
    assert len(conflicts) == 1
    assert conflicts[0].kind == "rpmnew"
    assert "-old = 1" in conflicts[0].diff
    assert "+old = 2" in conflicts[0].diff

    text = lt.format_rpm_conflicts(conflicts)
    assert "rpmconf" in text
    assert str(sibling) in text


def test_scan_rpm_conflicts_ignores_other_files(tmp_path: Path) -> None:
    (tmp_path / "sysctl.d").mkdir()
    (tmp_path / "sysctl.d" / "normal.conf").write_text("x = 1\n")
    assert lt.scan_rpm_conflicts(tmp_path) == ()


def test_report_splits_normal_and_aggressive(snapshot) -> None:
    data = snapshot(
        ncpu=1,
        intel_pstate=True,
        governors=(("powersave", 1),),
        epps=((0, "power"),),
        cpuidle=(lt.CpuIdleState(index=3, name="C3", latency_us=5000, disabled=False),),
    )
    report = lt.format_report(data, lt.evaluate(data))
    normal, aggressive = report.split("Aggressive tuning opportunities (--aggressive)", 1)
    normal_list = normal.split("Tuning opportunities", 1)[1]
    assert "cpu-epp" in normal_list
    assert "cpu-cstates" not in normal_list
    assert "cpu-cstates" in aggressive


def test_format_apply_results_marks_dry_run() -> None:
    results = lt.apply_runtime([lt.Write("/tmp/example", "1")], execute=False)
    text = lt.format_apply_results(results, executed=False)
    assert "dry run" in text
    assert "No runtime settings written" in text


def test_permanent_files_use_etc_paths(tmp_path: Path) -> None:
    findings = [
        lt.Finding(
            key="x",
            title="x",
            status="info",
            detail="x",
            sysctl=(("vm.page-cluster", "0"),),
            udev=('ACTION=="add", KERNEL=="x"',),
            service=("echo 1 > /sys/example",),
        )
    ]
    files = lt.permanent_files(findings, tmp_path)
    assert tmp_path / "sysctl.d" / lt.SYSCTL_CONF in files
    assert tmp_path / "udev" / "rules.d" / lt.UDEV_RULES in files
    assert tmp_path / "systemd" / "system" / lt.SERVICE_UNIT in files


def test_report_dict_is_json_serializable(snapshot) -> None:
    data = snapshot(
        host="test",
        ncpu=2,
        latency=lt.Latency(p50_us=100, p95_us=200, p99_us=300, max_us=400, samples=10),
    )
    findings = lt.evaluate(data)
    payload = lt.report_as_dict(data, findings)
    encoded = json.dumps(payload)
    assert "test" in encoded


def test_dataclasses_are_frozen(snapshot) -> None:
    written = lt.Write("/sys/example", "1")
    with pytest.raises(dataclasses.FrozenInstanceError):
        written.value = "2"  # type: ignore[misc]
