#!/usr/bin/env python3
"""Tests for wine.game.add."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

SCRIPT = Path(__file__).with_name("wine.game.add")
LOADER = SourceFileLoader("wine_game_add", str(SCRIPT))
SPEC = importlib.util.spec_from_loader("wine_game_add", LOADER)
wga = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(wga)


LUTRIS_SCHEMA = """
CREATE TABLE games (
    id INTEGER PRIMARY KEY,
    name TEXT,
    slug TEXT,
    installer_slug TEXT,
    parent_slug TEXT,
    platform TEXT,
    runner TEXT,
    executable TEXT,
    directory TEXT,
    updated DATETIME,
    lastplayed INTEGER,
    installed INTEGER,
    installed_at INTEGER,
    year INTEGER,
    configpath TEXT,
    has_custom_banner INTEGER,
    has_custom_icon INTEGER,
    playtime REAL,
    hidden INTEGER,
    service TEXT,
    service_id TEXT,
    sortname TEXT,
    has_custom_coverart_big INTEGER,
    discord_id TEXT
);
CREATE TABLE categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);
CREATE TABLE games_categories (game_id INTEGER, category_id INTEGER);
"""


@pytest.fixture
def isolated_home(tmp_path, monkeypatch):
    """Point every launcher path at a throwaway home directory."""
    home = tmp_path / "home"
    heroic = home / ".config" / "heroic"
    lutris_config = home / ".config" / "lutris"
    lutris_data = home / ".local" / "share" / "lutris"
    (heroic / "store").mkdir(parents=True)
    (heroic / "GamesConfig").mkdir()
    (lutris_config / "games").mkdir(parents=True)
    lutris_data.mkdir(parents=True)

    monkeypatch.setattr(wga, "HOME", home)
    monkeypatch.setattr(wga, "HEROIC_DIR", heroic)
    monkeypatch.setattr(wga, "LUTRIS_CONFIG", lutris_config)
    monkeypatch.setattr(wga, "LUTRIS_DATA", lutris_data)
    monkeypatch.setattr(wga, "LUTRIS_DATABASE", lutris_data / "pga.db")
    monkeypatch.setattr(wga, "HEROIC_LIBRARY", heroic / "sideload_apps" / "library.json")
    monkeypatch.setattr(wga, "HEROIC_GAMES_CONFIG", heroic / "GamesConfig")
    monkeypatch.setattr(wga, "HEROIC_STORE_CONFIG", heroic / "store" / "config.json")
    monkeypatch.setenv("WINEPREFIX", "")
    return home


def write_executable(path: Path, size: int = 1024) -> Path:
    """Create a fake executable of the requested size."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)
    return path


def make_prefix(root: Path, pfx_layout: bool = False) -> Path:
    """Create a prefix with drive_c and return the Wine prefix."""
    prefix = root / "pfx" if pfx_layout else root
    (prefix / "drive_c").mkdir(parents=True)
    return prefix


def options(**overrides) -> SimpleNamespace:
    """Build the option namespace used by the add functions."""
    values = {"force": False, "dry_run": False, "verbose": False}
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("setup_cyberpunk_2077_2.3_(64bit)_(83622).exe", "Cyberpunk 2077"),
        ("BusSimulator21-Win64-Shipping.exe", "Bus Simulator 21"),
        ("TheWitcher3", "The Witcher 3"),
        ("Monument Valley.exe", "Monument Valley"),
        ("Cyberpunk2077", "Cyberpunk 2077"),
        ("[GOG] Cyberpunk 2077", "Cyberpunk 2077"),
        ("CitizenSleeperXbYLR", "Citizen Sleeper"),
        ("TheDarksideDetectivehsD4J", "The Darkside Detective"),
        ("KatanaZERO", "Katana ZERO"),
        ("FIFA23", "FIFA 23"),
        ("HalfLife2", "Half Life 2"),
    ],
)
def test_clean_title(value, expected):
    assert wga.clean_title(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("CitizenSleeperXbYLR", "CitizenSleeper"),
        ("TheDarksideDetectivehsD4J", "TheDarksideDetective"),
        ("ThiefvWwV2", "Thief"),
        ("MortalShell", "MortalShell"),
        ("AerialKnightsNeverYield", "AerialKnightsNeverYield"),
        ("DokiDokiLitClubPlus", "DokiDokiLitClubPlus"),
        ("Cyberpunk2077", "Cyberpunk2077"),
        ("PAYDAY2", "PAYDAY2"),
    ],
)
def test_strip_random_suffix(value, expected):
    assert wga.strip_random_suffix(value) == expected


def test_infer_title_prefers_descriptive_exe_stem(tmp_path):
    exe = write_executable(tmp_path / "CitizenSleeperXbYLR" / "Citizen Sleeper.exe")
    assert wga.infer_title(exe) == "Citizen Sleeper"


def test_infer_title_uses_folder_for_helper_exe(tmp_path):
    exe = write_executable(tmp_path / "TheWitcher3" / "redprelauncher.exe")
    assert wga.infer_title(exe) == "The Witcher 3"


def test_infer_title_uses_gog_metadata(tmp_path):
    game_dir = tmp_path / "SomeGame"
    game_dir.mkdir()
    (game_dir / "goggame-1.info").write_text(
        json.dumps(
            {
                "gameId": "1",
                "rootGameId": "1",
                "name": "The Real Title",
                "playTasks": [
                    {"type": "FileTask", "path": "Game.exe", "isPrimary": True}
                ],
            }
        ),
        encoding="utf-8",
    )
    exe = write_executable(game_dir / "Game.exe")
    assert wga.infer_title(exe) == "The Real Title"


def test_detect_prefix(tmp_path):
    prefix = make_prefix(tmp_path / "Prefix")
    exe = write_executable(prefix / "drive_c" / "GOG Games" / "Game" / "Game.exe")
    assert wga.detect_prefix(exe) == prefix


def test_detect_prefix_keeps_pfx_layout(tmp_path):
    prefix = make_prefix(tmp_path / "Prefix", pfx_layout=True)
    exe = write_executable(prefix / "drive_c" / "GOG Games" / "Game" / "Game.exe")
    assert wga.detect_prefix(exe) == prefix


def test_infer_install_root_climbs_generic_directories(tmp_path):
    prefix = make_prefix(tmp_path / "Prefix")
    exe = write_executable(prefix / "drive_c" / "GOG Games" / "Title" / "bin" / "Game.exe")
    assert wga.infer_install_root(exe, prefix) == prefix / "drive_c" / "GOG Games" / "Title"


def test_find_installed_exe_skips_helpers(tmp_path):
    prefix = make_prefix(tmp_path / "Prefix", pfx_layout=True)
    game = prefix / "drive_c" / "GOG Games" / "Test Game"
    write_executable(game / "Game.exe", 2_000_000)
    main = write_executable(game / "bin" / "TestGame-Win64-Shipping.exe", 8_000_000)
    write_executable(game / "UnityCrashHandler64.exe", 9_000_000)
    write_executable(game / "unins000.exe", 9_000_000)
    write_executable(game / "_CommonRedist" / "vcredist_x64.exe", 9_000_000)
    write_executable(prefix / "drive_c" / "Program Files" / "Other" / "Other.exe", 20_000_000)

    found, shortlist = wga.find_installed_exe(prefix, "Test Game", set())

    assert found == main
    assert shortlist


def test_find_installed_exe_prefers_new_files(tmp_path):
    prefix = make_prefix(tmp_path / "Prefix")
    game = prefix / "drive_c" / "GOG Games" / "Test Game"
    old = write_executable(game / "OldGame.exe", 20_000_000)
    new = write_executable(game / "NewGame.exe", 1_000_000)

    found, _ = wga.find_installed_exe(prefix, "Test Game", {old})

    assert found == new


def test_add_heroic_writes_library_and_config(isolated_home):
    prefix = make_prefix(isolated_home / "Prefixes" / "Test Game", pfx_layout=True)
    exe = write_executable(prefix / "drive_c" / "GOG Games" / "Test Game" / "Game.exe")
    directory = exe.parent
    runner = wga.Runner(
        kind="proton",
        binary="/bin/true",
        name="Proton Test",
        wine_version={"bin": "/bin/true", "name": "Proton Test", "type": "proton"},
    )
    game = wga.Game(
        target=exe,
        title="Test Game",
        exe=exe,
        directory=directory,
        install_dir=directory,
        prefix=prefix,
        args=["-windowed"],
        gog=None,
    )

    assert wga.add_heroic(game, runner, options(), prefix) == 0

    library = json.loads(wga.HEROIC_LIBRARY.read_text(encoding="utf-8"))
    record = library["games"][0]
    assert record["title"] == "Test Game"
    assert record["install"]["executable"] == str(exe)
    assert record["folder_name"] == str(directory)
    assert record["is_installed"] is True

    config_path = wga.HEROIC_GAMES_CONFIG / f"{record['app_name']}.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    app_config = config[record["app_name"]]
    assert app_config["winePrefix"] == str(prefix.parent)
    assert app_config["wineVersion"]["type"] == "proton"
    assert app_config["launcherArgs"] == "-windowed"


def test_add_heroic_requires_force_to_update(isolated_home):
    prefix = make_prefix(isolated_home / "Prefixes" / "Game")
    exe = write_executable(prefix / "drive_c" / "GOG Games" / "Game" / "Game.exe")
    runner = wga.Runner(kind="wine", binary="/bin/true", name="Wine")
    game = wga.Game(
        target=exe,
        title="Game",
        exe=exe,
        directory=exe.parent,
        install_dir=exe.parent,
        prefix=prefix,
        args=[],
        gog=None,
    )

    assert wga.add_heroic(game, runner, options(), prefix) == 0
    with pytest.raises(SystemExit):
        wga.add_heroic(game, runner, options(), prefix)

    assert wga.add_heroic(game, runner, options(force=True), prefix) == 0
    library = json.loads(wga.HEROIC_LIBRARY.read_text(encoding="utf-8"))
    assert len(library["games"]) == 1


def test_add_lutris_writes_yaml_and_database(isolated_home):
    with sqlite3.connect(wga.LUTRIS_DATABASE) as connection:
        connection.executescript(LUTRIS_SCHEMA)

    prefix = make_prefix(isolated_home / "Games" / "Test Game")
    exe = write_executable(prefix / "drive_c" / "GOG Games" / "Test Game" / "Game.exe")
    directory = prefix / "drive_c" / "GOG Games" / "Test Game"
    runner = wga.Runner(kind="wine", binary="/bin/true", name="Wine Test", version="wine-test")
    game = wga.Game(
        target=exe,
        title="Test Game",
        exe=exe,
        directory=prefix,
        install_dir=directory,
        prefix=prefix,
        args=["-windowed"],
        gog=None,
    )

    assert wga.add_lutris(game, runner, options(), prefix) == 0

    rows = wga.lutris_rows()
    assert len(rows) == 1
    row = rows[0]
    assert row["name"] == "Test Game"
    assert row["runner"] == "wine"
    assert row["directory"] == str(prefix)

    config_path = wga.lutris_config_file(row["configpath"])
    assert config_path is not None and config_path.is_file()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert config["game"]["exe"] == str(exe)
    assert config["game"]["prefix"] == str(prefix)
    assert config["game"]["args"] == "-windowed"
    assert config["wine"]["version"] == "wine-test"


def test_adjust_runner_uses_wine_for_plain_prefix(isolated_home, monkeypatch):
    prefix = make_prefix(isolated_home / "Prefix")
    wga.HEROIC_STORE_CONFIG.write_text(
        json.dumps(
            {
                "settings": {
                    "wineVersion": {"bin": "/bin/true", "name": "Proton", "type": "proton"}
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(wga, "system_wine", lambda: "/bin/true")
    runner = wga.Runner(kind="proton", binary="/bin/true", name="Proton")
    adjusted = wga.adjust_runner_for_prefix(
        runner,
        prefix,
        "heroic",
        SimpleNamespace(install=False, wine=None, proton=None, runner=None),
    )
    assert adjusted.kind == "wine"


def test_adjust_runner_keeps_proton_for_pfx_prefix(isolated_home):
    prefix = make_prefix(isolated_home / "Prefix", pfx_layout=True)
    wga.HEROIC_STORE_CONFIG.write_text(
        json.dumps(
            {
                "settings": {
                    "wineVersion": {"bin": "/bin/true", "name": "Proton", "type": "proton"}
                }
            }
        ),
        encoding="utf-8",
    )
    runner = wga.Runner(kind="wine", binary="/bin/true", name="Wine")
    adjusted = wga.adjust_runner_for_prefix(
        runner,
        prefix,
        "heroic",
        SimpleNamespace(install=False, wine=None, proton=None, runner=None),
    )
    assert adjusted.kind == "proton"


def test_main_dry_run_does_not_write(isolated_home, monkeypatch):
    prefix = make_prefix(isolated_home / "Prefixes" / "Game")
    exe = write_executable(prefix / "drive_c" / "GOG Games" / "Game" / "Game.exe")
    wga.HEROIC_STORE_CONFIG.write_text(
        json.dumps(
            {
                "settings": {
                    "wineVersion": {"bin": "/bin/true", "name": "Test Wine", "type": "wine"}
                }
            }
        ),
        encoding="utf-8",
    )

    assert wga.main(["--dry-run", "--launcher", "heroic", str(exe)]) == 0
    assert not wga.HEROIC_LIBRARY.exists()

    assert wga.main(["--launcher", "heroic", str(exe)]) == 0
    assert wga.HEROIC_LIBRARY.is_file()
