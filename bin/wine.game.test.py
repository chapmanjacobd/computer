#!/usr/bin/env python3
"""Tests for wine.game."""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("wine.game")
LOADER = SourceFileLoader("wine_game", str(SCRIPT))
SPEC = importlib.util.spec_from_loader("wine_game", LOADER)
wg = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(wg)


def write_file(path: Path, content: bytes = b"x") -> Path:
    """Create a file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def make_launch(tmp_path: Path, args: list[str] | None = None) -> wg.Launch:
    """Build a Wine launch with a game inside a prefix."""
    prefix = tmp_path / "prefix"
    game_dir = prefix / "drive_c" / "Games" / "Demo"
    game_exe = write_file(game_dir / "Demo.exe")
    return wg.Launch(
        source="heroic",
        label='Heroic (sideload) "Demo"',
        kind="wine",
        runner="/bin/true",
        prefix=str(prefix),
        workdir=str(game_dir),
        env={"WINEPREFIX": str(prefix)},
        args=args or [],
        store="heroic/sideload",
        title="Demo",
        runner_label="Wine",
        game_exe=str(game_exe),
        install_dir=str(game_dir),
    )


def test_resolve_run_program_absolute(tmp_path):
    launch = make_launch(tmp_path)
    program = write_file(tmp_path / "Downloads" / "update.exe")

    assert Path(wg.resolve_run_program(str(program), launch)) == program.resolve()


def test_resolve_run_program_relative_to_game_directory(tmp_path, monkeypatch):
    launch = make_launch(tmp_path)
    program = write_file(Path(launch.install_dir) / "tools" / "alt.exe")
    monkeypatch.chdir(tmp_path)

    assert Path(wg.resolve_run_program("tools/alt.exe", launch)) == program.resolve()


def test_resolve_run_program_relative_to_prefix_drive_c(tmp_path, monkeypatch):
    launch = make_launch(tmp_path)
    program = write_file(Path(launch.prefix) / "drive_c" / "Tools" / "updater.exe")
    monkeypatch.chdir(tmp_path)

    assert (
        Path(wg.resolve_run_program("Tools/updater.exe", launch)) == program.resolve()
    )


def test_resolve_run_program_accepts_windows_separators(tmp_path, monkeypatch):
    launch = make_launch(tmp_path)
    program = write_file(Path(launch.install_dir) / "tools" / "alt.exe")
    monkeypatch.chdir(tmp_path)

    assert Path(wg.resolve_run_program(r"tools\alt.exe", launch)) == program.resolve()


def test_resolve_run_program_reports_missing(tmp_path):
    launch = make_launch(tmp_path)

    with pytest.raises(SystemExit):
        wg.resolve_run_program("missing-update.exe", launch)


def test_launch_command_skips_saved_game_args(tmp_path):
    launch = make_launch(tmp_path, args=["-saved"])

    command = launch.command(
        "alt.exe", ["-explicit"], gamemode=False, include_args=False
    )

    assert command == ["/bin/true", "alt.exe", "-explicit"]


def test_main_run_uses_matched_game_environment(tmp_path, monkeypatch, capsys):
    launch = make_launch(tmp_path, args=["-saved"])
    program = write_file(tmp_path / "Downloads" / "update.exe")
    monkeypatch.setattr(wg, "collect_launches", lambda: [launch])
    monkeypatch.setattr(wg, "GAMEMODERUN", None)

    code = wg.main(
        [
            "--dry-run",
            "--no-gamemode",
            "--quiet",
            "--run",
            str(program),
            launch.game_exe,
            "-explicit",
        ]
    )

    assert code == 0
    out = capsys.readouterr().out
    assert str(program) in out
    assert "-explicit" in out
    assert "-saved" not in out


def test_main_run_requires_a_game_selector(tmp_path, monkeypatch):
    program = write_file(tmp_path / "Downloads" / "update.exe")
    monkeypatch.setattr(wg, "collect_launches", list)

    with pytest.raises(SystemExit):
        wg.main(["--run", str(program)])


def test_main_rejects_run_after_game_selector(tmp_path, monkeypatch):
    launch = make_launch(tmp_path)
    program = write_file(tmp_path / "Downloads" / "update.exe")
    monkeypatch.setattr(wg, "collect_launches", lambda: [launch])

    with pytest.raises(SystemExit):
        wg.main([launch.game_exe, "--run", str(program)])


def test_main_passes_run_game_argument_after_separator(tmp_path, monkeypatch, capsys):
    launch = make_launch(tmp_path)
    monkeypatch.setattr(wg, "collect_launches", lambda: [launch])
    monkeypatch.setattr(wg, "GAMEMODERUN", None)

    code = wg.main(
        [
            "--dry-run",
            "--no-gamemode",
            "--quiet",
            launch.game_exe,
            "--",
            "--run",
            "value",
        ]
    )

    assert code == 0
    assert "--run value" in capsys.readouterr().out
