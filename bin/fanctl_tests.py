#!/usr/bin/env pytest
# SPDX-License-Identifier: WTFPL

"""Tests for fanctl."""

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).with_name("fanctl")
_LOADER = importlib.machinery.SourceFileLoader("fanctl", str(_SCRIPT))
_SPEC = importlib.util.spec_from_loader("fanctl", _LOADER)
assert _SPEC is not None
fc = importlib.util.module_from_spec(_SPEC)
sys.modules["fanctl"] = fc
_LOADER.exec_module(fc)


def make_chip(root: Path, dirname: str, name: str, **files: object) -> Path:
    """Create a fake hwmon device with one attribute per keyword argument."""
    device = root / dirname
    device.mkdir(parents=True)
    (device / "name").write_text(f"{name}\n")
    for filename, value in files.items():
        (device / filename).write_text(f"{value}\n")
    return device


def find(channels: list[fc.Channel], key: str) -> fc.Channel:
    return next(channel for channel in channels if channel.key == key)


def test_discover_maps_pwm_fan_and_temperature(tmp_path: Path) -> None:
    make_chip(
        tmp_path,
        "hwmon0",
        "nct6798",
        pwm1=128,
        pwm1_enable=1,
        pwm1_temp_sel=2,
        pwm2=200,
        pwm2_enable=5,
        pwm2_temp_sel=7,
        fan1_input=1200,
        fan2_input=0,
        temp2_label="SYSTIN",
        temp2_input=26000,
        temp7_label="PECI Agent 0",
        temp7_input=66500,
    )
    channels = fc.discover(tmp_path)
    assert len(channels) == 2

    manual = find(channels, "nct6798:1")
    assert manual.value == 128
    assert manual.enable == 1
    assert manual.fan_rpm == 1200
    assert manual.temp_label == "SYSTIN"
    assert manual.temp_value == 26000
    assert manual.key == "nct6798:1"

    auto = find(channels, "nct6798:2")
    assert auto.enable == 5
    assert auto.fan_rpm == 0
    assert auto.temp_label == "PECI Agent 0"
    assert auto.temp_value == 66500


def test_discover_ignores_non_channel_pwm_files(tmp_path: Path) -> None:
    make_chip(
        tmp_path,
        "hwmon0",
        "nct6798",
        pwm1=100,
        pwm1_enable=1,
        pwm1_auto_point1_pwm=153,
        pwm1_auto_point1_temp=30000,
        pwm2_enable=5,  # enable without pwm must not become a channel
    )
    channels = fc.discover(tmp_path)
    assert [channel.pwm for channel in channels] == [1]


def test_discover_uses_plain_temp_name_when_label_missing(tmp_path: Path) -> None:
    make_chip(tmp_path, "hwmon0", "amdgpu", pwm1=90, pwm1_enable=1, temp1_input=37000)
    channels = fc.discover(tmp_path)
    assert channels[0].temp_label is None
    assert channels[0].temp_value is None


@pytest.mark.parametrize(
    ("percent", "expected"),
    [(0, 0), (1, 3), (33, 84), (50, 128), (99, 252), (100, 255)],
)
def test_percent_to_pwm(percent: int, expected: int) -> None:
    assert fc.percent_to_pwm(percent) == expected


@pytest.mark.parametrize(
    ("text", "raw", "expected"),
    [
        ("50%", False, 128),
        ("50%", True, 128),
        ("0%", False, 0),
        ("100%", False, 255),
        ("50", False, 128),
        ("0", False, 0),
        ("100", False, 255),
        ("128", True, 128),
        ("255", True, 255),
    ],
)
def test_parse_duty(text: str, raw: bool, expected: int) -> None:
    assert fc.parse_duty(text, raw=raw) == expected


@pytest.mark.parametrize("text", ["101", "256", "-1", "banana", "151%"])
def test_parse_duty_rejects_invalid(text: str) -> None:
    with pytest.raises(ValueError):
        fc.parse_duty(text)


def test_parse_duty_allows_full_raw_range_only_with_raw() -> None:
    with pytest.raises(ValueError):
        fc.parse_duty("255", raw=False)
    assert fc.parse_duty("255", raw=True) == 255


@pytest.mark.parametrize(
    ("enable", "expected"),
    [
        (0, "max"),
        (1, "manual"),
        (2, "thermal"),
        (3, "speed"),
        (5, "smart IV"),
        (9, "mode 9"),
    ],
)
def test_mode_label(enable: int | None, expected: str) -> None:
    assert fc.mode_label(enable) == expected


def test_resolve_target_accepts_common_spellings(tmp_path: Path) -> None:
    make_chip(tmp_path, "hwmon0", "nct6798", pwm2=1, pwm2_enable=1)
    channels = fc.discover(tmp_path)
    for target in ("2", "pwm2", "nct6798:2", "nct6798/pwm2", "hwmon0:2", "hwmon0/pwm2"):
        assert fc.resolve_target(target, channels).key == "nct6798:2"


def test_resolve_target_rejects_ambiguous_index(tmp_path: Path) -> None:
    make_chip(tmp_path, "hwmon0", "nct6798", pwm1=1, pwm1_enable=1)
    make_chip(tmp_path, "hwmon1", "amdgpu", pwm1=1, pwm1_enable=1)
    channels = fc.discover(tmp_path)
    with pytest.raises(ValueError, match="ambiguous"):
        fc.resolve_target("1", channels)
    assert fc.resolve_target("amdgpu:1", channels).key == "amdgpu:1"


def test_resolve_target_reports_missing(tmp_path: Path) -> None:
    make_chip(tmp_path, "hwmon0", "nct6798", pwm1=1, pwm1_enable=1)
    channels = fc.discover(tmp_path)
    with pytest.raises(ValueError, match="no channel"):
        fc.resolve_target("nct6798:7", channels)


def test_set_manual_writes_mode_before_duty(tmp_path: Path) -> None:
    device = make_chip(tmp_path, "hwmon0", "nct6798", pwm1=10, pwm1_enable=5)
    channel = fc.discover(tmp_path)[0]
    fc.set_manual(channel, 64)
    assert (device / "pwm1_enable").read_text().strip() == "1"
    assert (device / "pwm1").read_text().strip() == "64"


def test_set_manual_rejects_out_of_range(tmp_path: Path) -> None:
    make_chip(tmp_path, "hwmon0", "nct6798", pwm1=10, pwm1_enable=1)
    channel = fc.discover(tmp_path)[0]
    with pytest.raises(ValueError, match="0..255"):
        fc.set_manual(channel, 256)


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        ({"pwm1": 1, "pwm1_enable": 5, "pwm1_auto_point1_pwm": 100}, 5),
        ({"pwm1": 1, "pwm1_enable": 2, "pwm1_target_temp": 50000}, 2),
        ({"pwm1": 1, "pwm1_enable": 1}, 2),
    ],
)
def test_auto_mode_for(tmp_path: Path, files: dict[str, int], expected: int) -> None:
    make_chip(tmp_path, "hwmon0", "nct6798", **files)
    channel = fc.discover(tmp_path)[0]
    assert fc.auto_mode_for(channel) == expected


def test_snapshot_keeps_only_manual_channels(tmp_path: Path) -> None:
    make_chip(
        tmp_path,
        "hwmon0",
        "nct6798",
        pwm1=64,
        pwm1_enable=1,
        pwm2=100,
        pwm2_enable=5,
    )
    channels = fc.discover(tmp_path)
    snapshot = fc.snapshot_channels(channels)
    assert snapshot == [{"chip": "nct6798", "pwm": 1, "enable": 1, "value": 64}]


def test_snapshot_roundtrip(tmp_path: Path) -> None:
    state = tmp_path / "boot.json"
    snapshot = [{"chip": "nct6798", "pwm": 2, "enable": 1, "value": 128}]
    fc.write_snapshot(state, snapshot)
    assert fc.read_snapshot(state) == snapshot


def test_read_snapshot_missing_and_corrupt(tmp_path: Path) -> None:
    assert fc.read_snapshot(tmp_path / "absent.json") == []
    broken = tmp_path / "broken.json"
    broken.write_text("{not json")
    assert fc.read_snapshot(broken) == []


def test_upsert_snapshot_replaces_channel() -> None:
    snapshot = [{"chip": "nct6798", "pwm": 1, "enable": 1, "value": 10}]
    updated = fc.upsert_snapshot(
        snapshot, {"chip": "nct6798", "pwm": 1, "enable": 1, "value": 99}
    )
    assert updated == [{"chip": "nct6798", "pwm": 1, "enable": 1, "value": 99}]
