#!/usr/bin/env pytest
# SPDX-License-Identifier: WTFPL

"""Tests for path_conflicts.py."""

import os
from pathlib import Path

import pytest

import path_conflicts as pc


def make_exec(path: Path, body: str = "#!/bin/sh\nexit 0\n") -> Path:
    path.write_text(body)
    path.chmod(0o755)
    return path


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", []),
        ("/a:/b", ["/a", "/b"]),
        ("/a:/b:/a", ["/a", "/b"]),
        ("/a/:/a//:/b/", ["/a", "/b"]),
        (":/a::/b:", ["/a", "/b"]),
    ],
)
def test_split_path_dedupes_and_preserves_order(
    value: str, expected: list[str]
) -> None:
    assert pc.split_path(value) == expected


def test_split_path_resolves_relative_entries(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert pc.split_path("bin:bin") == [str(tmp_path / "bin")]


def test_path_dirs_dedupes_symlinked_dirs(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(real)
    dirs = pc.path_dirs(f"{real}:{alias}", home=str(tmp_path / "home"))
    assert [d.path for d in dirs] == [str(real)]
    assert dirs[0].real == str(real)


def test_path_dirs_classifies_user_and_system(tmp_path: Path) -> None:
    home = tmp_path / "home"
    user = home / ".local" / "bin"
    user.mkdir(parents=True)
    system = tmp_path / "usr" / "bin"
    system.mkdir(parents=True)
    dirs = pc.path_dirs(f"{user}:{system}", home=str(home))
    assert [(d.path, d.kind) for d in dirs] == [
        (str(user), "user"),
        (str(system), "system"),
    ]


def test_path_dirs_skips_missing_directories(tmp_path: Path) -> None:
    assert pc.path_dirs(str(tmp_path / "nope"), home=str(tmp_path)) == []


def test_path_dirs_numbers_resolved_entries_in_order(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(second)

    dirs = pc.path_dirs(f"{first}:{second}:{alias}", home=str(tmp_path / "home"))

    assert [(d.real, d.order) for d in dirs] == [
        (str(first), 0),
        (str(second), 1),
    ]


def test_iter_commands_lists_executables(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_exec(bin_dir / "alpha")
    (bin_dir / "plain").write_text("not executable")
    os.symlink(bin_dir / "alpha", bin_dir / "alias")
    os.symlink(bin_dir / "gone", bin_dir / "broken")
    (bin_dir / "subdir").mkdir()
    assert pc.iter_commands(str(bin_dir)) == ["alias", "alpha"]


def test_scan_separates_conflicts_from_unique_names(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    make_exec(first / "shared")
    make_exec(second / "shared")
    make_exec(first / "only")
    dirs = pc.path_dirs(f"{first}:{second}", home=str(tmp_path / "home"))
    index = pc.scan(dirs)
    assert set(pc.conflicting(index)) == {"shared"}
    assert set(pc.non_conflicting(index)) == {"only"}


def test_scan_treats_two_names_for_one_file_as_non_conflicting(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    make_exec(first / "tool")
    os.symlink(first / "tool", second / "tool")
    dirs = pc.path_dirs(f"{first}:{second}", home=str(tmp_path / "home"))
    index = pc.scan(dirs)
    assert pc.conflicting(index) == {}
    assert set(pc.non_conflicting(index)) == {"tool"}


def test_render_conflict_marks_first_path_as_winner(tmp_path: Path) -> None:
    one = pc.PathDir(
        path=str(tmp_path / "one"), real=str(tmp_path / "one"), kind="user"
    )
    two = pc.PathDir(
        path=str(tmp_path / "two"), real=str(tmp_path / "two"), kind="system"
    )
    occurrences = [
        pc.Occurrence(
            name="tool",
            path_dir=one,
            file=f"{one.path}/tool",
            real=f"{one.path}/tool",
            version="tool 1.0",
            package="user install",
        ),
        pc.Occurrence(
            name="tool",
            path_dir=two,
            file=f"{two.path}/tool",
            real=f"{two.path}/tool",
            version="tool 2.0",
            package="tool-pkg 2.0-1",
        ),
    ]
    text = pc.render_conflict("tool", occurrences, tablefmt="simple")
    assert text.splitlines()[0] == "tool"
    winner_line = next(line for line in text.splitlines() if one.path in line)
    loser_line = next(line for line in text.splitlines() if two.path in line)
    assert "*" in winner_line
    assert "*" not in loser_line
    assert "tool 2.0" in text
    assert "tool-pkg 2.0-1" in text


def test_render_conflict_uses_resolved_paths_in_resolution_order(
    tmp_path: Path,
) -> None:
    late = pc.PathDir(
        path=str(tmp_path / "late-alias"),
        real=str(tmp_path / "late-real"),
        kind="system",
        order=1,
    )
    early = pc.PathDir(
        path=str(tmp_path / "early-alias"),
        real=str(tmp_path / "early-real"),
        kind="user",
        order=0,
    )
    occurrences = [
        pc.Occurrence("tool", late, f"{late.path}/tool", f"{late.real}/tool"),
        pc.Occurrence("tool", early, f"{early.path}/tool", f"{early.real}/tool"),
    ]

    text = pc.render_conflict("tool", occurrences, tablefmt="simple")

    assert late.path not in text
    assert early.path not in text
    assert text.index(early.real) < text.index(late.real)
    winner_line = next(line for line in text.splitlines() if early.real in line)
    loser_line = next(line for line in text.splitlines() if late.real in line)
    assert "*" in winner_line
    assert "*" not in loser_line


def test_render_non_conflicting_groups_by_path(tmp_path: Path) -> None:
    one = pc.PathDir(
        path=str(tmp_path / "one"), real=str(tmp_path / "one"), kind="user"
    )
    two = pc.PathDir(
        path=str(tmp_path / "two"), real=str(tmp_path / "two"), kind="system"
    )
    index = {
        "alpha": [
            pc.Occurrence("alpha", one, f"{one.path}/alpha", f"{one.path}/alpha")
        ],
        "beta": [pc.Occurrence("beta", two, f"{two.path}/beta", f"{two.path}/beta")],
    }
    text = pc.render_non_conflicting([one, two], index, tablefmt="simple")
    assert one.path in text
    assert two.path in text
    assert "alpha" in text
    assert "beta" in text


def test_render_non_conflicting_uses_resolved_paths_in_resolution_order(
    tmp_path: Path,
) -> None:
    late = pc.PathDir(
        path=str(tmp_path / "late-alias"),
        real=str(tmp_path / "late-real"),
        kind="system",
        order=1,
    )
    early = pc.PathDir(
        path=str(tmp_path / "early-alias"),
        real=str(tmp_path / "early-real"),
        kind="user",
        order=0,
    )
    index = {
        "alpha": [
            pc.Occurrence("alpha", late, f"{late.path}/alpha", f"{late.path}/alpha")
        ],
        "beta": [
            pc.Occurrence("beta", early, f"{early.path}/beta", f"{early.path}/beta")
        ],
    }

    text = pc.render_non_conflicting([late, early], index, tablefmt="simple")

    assert late.path not in text
    assert early.path not in text
    assert text.index(early.real) < text.index(late.real)


@pytest.mark.parametrize(
    ("body", "timeout", "expected"),
    [
        ("#!/bin/sh\necho 'tool 1.2.3'\n", 5.0, "tool 1.2.3"),
        ("#!/bin/sh\necho first\necho second\n", 5.0, "first"),
        ("#!/bin/sh\necho 'oops' >&2\nexit 2\n", 5.0, ""),
        ("#!/bin/sh\necho 'usage' >&2\nexit 0\n", 5.0, "usage"),
        ("#!/bin/sh\nexit 0\n", 5.0, ""),
        ("#!/bin/sh\nsleep 5\n", 0.2, ""),
    ],
)
def test_probe_version(
    tmp_path: Path, body: str, timeout: float, expected: str
) -> None:
    executable = make_exec(tmp_path / "tool", body)
    assert pc.probe_version(str(executable), timeout=timeout) == expected


def test_rpm_info_parses_stub_output(tmp_path: Path) -> None:
    stub = make_exec(tmp_path / "rpm", "#!/bin/sh\nprintf 'bash 5.2.1-1.fc45\\n'\n")
    assert pc.rpm_info("/usr/bin/bash", rpm=str(stub)) == ("bash", "5.2.1-1.fc45")


def test_rpm_info_returns_empty_on_failure(tmp_path: Path) -> None:
    stub = make_exec(tmp_path / "rpm", "#!/bin/sh\nexit 1\n")
    assert pc.rpm_info("/usr/bin/bash", rpm=str(stub)) == ("", "")


def test_enrich_probes_the_path_entry_not_the_symlink_target(tmp_path: Path) -> None:
    target = make_exec(
        tmp_path / "dispatcher",
        '#!/bin/sh\necho "called-as $(basename "$0")"\n',
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    os.symlink(target, bin_dir / "alias")
    dirs = pc.path_dirs(str(bin_dir), home=str(tmp_path / "home"))
    index = pc.scan(dirs)

    pc.enrich(index, versions=True, packages=False, jobs=1)

    assert index["alias"][0].version == "called-as alias"


def test_package_label_queries_rpm_with_unresolved_path(tmp_path: Path) -> None:
    stub = make_exec(
        tmp_path / "rpm",
        "#!/bin/sh\nfor last; do :; done\nprintf 'pkg %s\\n' \"$last\"\n",
    )
    link = tmp_path / "link"
    os.symlink("/usr/bin/bash", link)

    label = pc.package_label(str(link), home=str(tmp_path / "home"), rpm=str(stub))

    assert label == f"pkg {link}"


def test_package_label_for_user_install(tmp_path: Path) -> None:
    path = str(tmp_path / ".local" / "bin" / "tool")
    assert pc.package_label(path, home=str(tmp_path)) == "user install"


def test_package_label_uses_rpm_for_system_path(tmp_path: Path) -> None:
    stub = make_exec(tmp_path / "rpm", "#!/bin/sh\nprintf 'bash 5.2.1-1.fc45\\n'\n")
    label = pc.package_label(
        "/usr/bin/bash", home=str(tmp_path / "home"), rpm=str(stub)
    )
    assert label == "bash 5.2.1-1.fc45"


def test_main_prints_non_conflicting_then_conflicting(tmp_path: Path, capsys) -> None:
    one = tmp_path / "one"
    two = tmp_path / "two"
    one.mkdir()
    two.mkdir()
    make_exec(one / "shared", "#!/bin/sh\necho 'shared 1.0'\n")
    make_exec(two / "shared", "#!/bin/sh\necho 'shared 2.0'\n")
    make_exec(one / "solo")

    assert pc.main(["--path", f"{one}:{two}", "--no-packages"]) == 0
    out = capsys.readouterr().out
    assert "Non-conflicting" in out
    assert "Conflicting" in out
    assert out.index("Non-conflicting") < out.index("Conflicting")
    assert "solo" in out
    assert "shared 1.0" in out
    assert "shared 2.0" in out
