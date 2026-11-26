#!/usr/bin/env pytest
# SPDX-License-Identifier: WTFPL

"""Tests for which.pip."""

from __future__ import annotations

import doctest
import importlib.machinery
import importlib.util
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).with_name("which.pip")
_LOADER = importlib.machinery.SourceFileLoader("which_pip", str(_SCRIPT))
_SPEC = importlib.util.spec_from_loader("which_pip", _LOADER)
assert _SPEC is not None
wp = importlib.util.module_from_spec(_SPEC)
sys.modules["which_pip"] = wp
_LOADER.exec_module(wp)


def make_dist(
    site_packages: Path,
    name: str,
    version: str = "1.0",
    *,
    installer: str | None = "pip",
    files: Sequence[str] = (),
    top_level: str | None = None,
) -> Path:
    """Create a fake dist-info directory in ``site_packages``."""
    dist = site_packages / f"{name}-{version}.dist-info"
    dist.mkdir(parents=True)
    (dist / "METADATA").write_text(
        f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n"
    )
    if installer is not None:
        (dist / "INSTALLER").write_text(f"{installer}\n")
    if files:
        (dist / "RECORD").write_text("".join(f"{entry},,\n" for entry in files))
    if top_level is not None:
        (dist / "top_level.txt").write_text(f"{top_level}\n")
    return dist


def make_script(path: Path, body: str = "#!/usr/bin/python3\nprint('hi')\n") -> Path:
    """Create an executable script at ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(0o755)
    return path


def make_prefix(tmp_path: Path) -> tuple[Path, Path]:
    """Create a fake Python prefix and return ``(prefix, site_packages)``."""
    prefix = tmp_path / "prefix"
    site_packages = prefix / "lib" / "python3.12" / "site-packages"
    site_packages.mkdir(parents=True)
    return prefix, site_packages


def test_doctests_pass() -> None:
    result = doctest.testmod(wp)
    assert result.failed == 0


def test_resolve_target_finds_command_on_path(tmp_path: Path) -> None:
    script = make_script(tmp_path / "bin" / "demo-tool")

    resolved = wp.resolve_target("demo-tool", path=str(script.parent))

    assert resolved == script.resolve()


def test_resolve_target_accepts_existing_relative_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    script = make_script(tmp_path / "demo-tool")

    assert wp.resolve_target("demo-tool", path="") == script.resolve()


def test_resolve_target_returns_none_for_missing_command() -> None:
    assert (
        wp.resolve_target("definitely-not-installed-xyz", path="/nonexistent") is None
    )


def test_resolve_target_returns_none_for_broken_symlink(tmp_path: Path) -> None:
    link = tmp_path / "bin" / "demo-tool"
    link.parent.mkdir()
    link.symlink_to(tmp_path / "gone")

    assert wp.resolve_target(str(link)) is None


def test_roots_for_target_uses_bin_prefix(tmp_path: Path) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    script = make_script(prefix / "bin" / "demo-tool")

    assert site_packages.resolve() in wp.roots_for_target(script)


def test_roots_for_target_uses_python_shebang(tmp_path: Path) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    script = make_script(
        tmp_path / "other" / "bin" / "demo-tool",
        body=f"#!{prefix}/bin/python\nprint('hi')\n",
    )

    assert site_packages.resolve() in wp.roots_for_target(script)


def test_roots_for_target_ignores_uv_shebang(tmp_path: Path) -> None:
    script = make_script(
        tmp_path / "bin" / "demo-tool",
        body="#!/usr/bin/env -S uv run --script\nprint('hi')\n",
    )

    assert wp.roots_for_target(script) == []


def test_find_owners_matches_record_entry(tmp_path: Path) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    script = make_script(prefix / "bin" / "demo-tool")
    make_dist(
        site_packages,
        "demo-package",
        "1.2.3",
        installer="pip",
        files=["../../../bin/demo-tool", "demo/__init__.py"],
    )

    owners = wp.find_owners(script, [site_packages])

    assert len(owners) == 1
    owner = owners[0]
    assert owner.package == "demo-package"
    assert owner.version == "1.2.3"
    assert owner.installer == "pip"
    assert owner.location == str(site_packages.resolve())
    assert owner.file == "../../../bin/demo-tool"


def test_find_owners_follows_target_symlinks(tmp_path: Path) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    script = make_script(prefix / "bin" / "demo-tool")
    link = tmp_path / "link"
    link.symlink_to(script)
    make_dist(
        site_packages,
        "demo-package",
        files=["../../../bin/demo-tool"],
    )

    owners = wp.find_owners(link, [site_packages])

    assert [owner.package for owner in owners] == ["demo-package"]


def test_find_owners_ignores_other_files_with_the_same_name(
    tmp_path: Path,
) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    script = make_script(prefix / "bin" / "demo-tool")
    make_dist(
        site_packages,
        "demo-package",
        files=["../../../bin/other/demo-tool"],
    )

    assert wp.find_owners(script, [site_packages]) == []


def test_find_owners_deduplicates_symlinked_site_packages(
    tmp_path: Path,
) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    script = make_script(prefix / "bin" / "demo-tool")
    make_dist(site_packages, "demo-package", files=["../../../bin/demo-tool"])
    alias = tmp_path / "alias"
    alias.symlink_to(site_packages)

    owners = wp.find_owners(script, [site_packages, alias])

    assert [owner.package for owner in owners] == ["demo-package"]


def test_find_owners_reads_installed_files_txt(tmp_path: Path) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    script = make_script(prefix / "bin" / "demo-tool")
    dist = site_packages / "demo-package.egg-info"
    dist.mkdir()
    (dist / "PKG-INFO").write_text("Name: demo-package\nVersion: 2.0\n")
    (dist / "installed-files.txt").write_text("../../../bin/demo-tool\n")

    owners = wp.find_owners(script, [site_packages])

    assert [(owner.package, owner.version, owner.file) for owner in owners] == [
        ("demo-package", "2.0", "../../../bin/demo-tool")
    ]


def test_find_distributions_matches_name_substring(tmp_path: Path) -> None:
    _, site_packages = make_prefix(tmp_path)
    make_dist(site_packages, "btrfs", "15")
    make_dist(site_packages, "unrelated", "2.0")

    owners = wp.find_distributions("BTRF", [site_packages])

    assert [(owner.package, owner.version) for owner in owners] == [("btrfs", "15")]


def test_find_distributions_normalizes_dashes_and_underscores(
    tmp_path: Path,
) -> None:
    _, site_packages = make_prefix(tmp_path)
    make_dist(site_packages, "python-dateutil", "2.9")

    for query in ("python-dateutil", "Python_DateUtil"):
        owners = wp.find_distributions(query, [site_packages])
        assert [owner.package for owner in owners] == ["python-dateutil"]


def test_find_by_import_matches_top_level_module(tmp_path: Path) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    script = make_script(
        prefix / "bin" / "demo-tool",
        body="#!/usr/bin/python3\nfrom demo.cli import main\nmain()\n",
    )
    make_dist(site_packages, "demo-package", top_level="demo")

    owners = wp.find_by_import(script, [site_packages])

    assert [owner.package for owner in owners] == ["demo-package"]


def test_find_by_import_ignores_stdlib_modules(tmp_path: Path) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    script = make_script(
        prefix / "bin" / "demo-tool",
        body="#!/usr/bin/python3\nimport argparse\nimport os\n",
    )
    make_dist(site_packages, "argparse-package", top_level="argparse")

    assert wp.find_by_import(script, [site_packages]) == []


def test_lookup_falls_back_to_imports(tmp_path: Path) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    make_script(
        prefix / "bin" / "demo-tool",
        body="#!/usr/bin/python3\nimport demo\n",
    )
    make_dist(site_packages, "demo-package", top_level="demo")

    owners = wp.lookup(
        "demo-tool",
        path=str(prefix / "bin"),
        roots=[site_packages],
    )

    assert [owner.package for owner in owners] == ["demo-package"]
    assert owners[0].target == "demo-tool"


def test_lookup_prefers_file_ownership_over_imports(tmp_path: Path) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    make_script(
        prefix / "bin" / "demo-tool",
        body="#!/usr/bin/python3\nimport helper\n",
    )
    make_dist(site_packages, "owner", files=["../../../bin/demo-tool"])
    make_dist(site_packages, "helper", top_level="helper")

    owners = wp.lookup(
        "demo-tool",
        path=str(prefix / "bin"),
        roots=[site_packages],
    )

    assert [owner.package for owner in owners] == ["owner"]


def test_lookup_without_executable_searches_distribution_names(
    tmp_path: Path,
) -> None:
    _, site_packages = make_prefix(tmp_path)
    make_dist(site_packages, "btrfs", "15")

    owners = wp.lookup("btrfs", path="", roots=[site_packages])

    assert [owner.package for owner in owners] == ["btrfs"]


def test_main_prints_table(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    make_script(prefix / "bin" / "demo-tool")
    make_dist(
        site_packages,
        "demo-package",
        "1.2.3",
        files=["../../../bin/demo-tool"],
    )

    exit_code = wp.main(
        ["demo-tool"],
        path=str(prefix / "bin"),
        roots=[site_packages],
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "TARGET" in captured.out
    assert "demo-tool" in captured.out
    assert "demo-package" in captured.out
    assert "1.2.3" in captured.out
    assert "pip" in captured.out


def test_main_verbose_includes_record_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    make_script(prefix / "bin" / "demo-tool")
    make_dist(site_packages, "demo-package", files=["../../../bin/demo-tool"])

    exit_code = wp.main(
        ["--verbose", "demo-tool"],
        path=str(prefix / "bin"),
        roots=[site_packages],
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "FILE" in captured.out
    assert "../../../bin/demo-tool" in captured.out


def test_main_json_includes_owner_fields(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    prefix, site_packages = make_prefix(tmp_path)
    make_script(prefix / "bin" / "demo-tool")
    make_dist(site_packages, "demo-package", files=["../../../bin/demo-tool"])

    exit_code = wp.main(
        ["--json", "demo-tool"],
        path=str(prefix / "bin"),
        roots=[site_packages],
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload == [
        {
            "target": "demo-tool",
            "package": "demo-package",
            "version": "1.0",
            "installer": "pip",
            "location": str(site_packages.resolve()),
            "file": "../../../bin/demo-tool",
        }
    ]


def test_main_reports_missing_targets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = wp.main(
        ["missing-tool"],
        path=str(tmp_path / "empty"),
        roots=[tmp_path / "site-packages"],
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "missing-tool" in captured.err
    assert "not found" in captured.err


def test_main_package_flag_skips_command_lookup(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _, site_packages = make_prefix(tmp_path)
    make_dist(site_packages, "btrfs", "15")

    exit_code = wp.main(
        ["--package", "btrfs"],
        path="",
        roots=[site_packages],
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "btrfs" in captured.out
    assert "15" in captured.out
