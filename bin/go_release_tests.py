#!/usr/bin/env python3
"""Tests for go.release."""

from __future__ import annotations

import runpy
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

MODULE_PATH = Path(__file__).with_name("go.release")
go_release = SimpleNamespace(**runpy.run_path(str(MODULE_PATH)))

Version = go_release.Version


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1.2.3", "1.2.3"),
        ("v1.2.3", "1.2.3"),
        ("refs/tags/v1.2.3", "1.2.3"),
        ("1.2.3-alpha.1", "1.2.3-alpha.1"),
        ("1.2.3+build.5", "1.2.3+build.5"),
        ("1.2.3-rc.2+build.5", "1.2.3-rc.2+build.5"),
    ],
)
def test_parse_and_format(text: str, expected: str) -> None:
    assert str(Version.parse(text)) == expected


@pytest.mark.parametrize(
    "text",
    [
        "1.2",
        "1.2.3.4",
        "1.2.3-",
        "1.2.3+",
        "1.2.3-alpha..1",
        "01.2.3",
        "1.2.03",
        "1.2.3-alpha.01",
        "not-a-version",
    ],
)
def test_parse_rejects_invalid(text: str) -> None:
    with pytest.raises(ValueError):
        Version.parse(text)


@pytest.mark.parametrize(
    ("current", "level", "expected"),
    [
        ("1.2.3", "patch", "1.2.4"),
        ("1.2.3-alpha.1", "patch", "1.2.3"),
        ("1.2.3", "minor", "1.3.0"),
        ("1.2.3-alpha.1", "minor", "1.3.0"),
        ("1.2.3", "major", "2.0.0"),
        ("1.2.3-alpha.1", "major", "2.0.0"),
        ("1.2.3", "release", "1.2.3"),
        ("1.2.3-alpha.1", "release", "1.2.3"),
        ("1.2.3", "alpha", "1.2.4-alpha.1"),
        ("1.2.3-alpha.1", "alpha", "1.2.3-alpha.2"),
        ("1.2.3-alpha", "alpha", "1.2.3-alpha.1"),
        ("1.2.3-alpha.1", "beta", "1.2.3-beta.1"),
        ("1.2.3-beta.1", "rc", "1.2.3-rc.1"),
        ("1.2.3-rc.1", "rc", "1.2.3-rc.2"),
        ("1.2.3-rc.1", "alpha", "1.2.3-alpha.1"),
    ],
)
def test_bump(current: str, level: str, expected: str) -> None:
    assert str(go_release.bump(Version.parse(current), level)) == expected


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("1.0.0", "2.0.0", -1),
        ("2.0.0", "1.0.0", 1),
        ("1.2.3", "1.2.3", 0),
        ("1.2.3", "1.2.3+build", 0),
        ("1.2.3-alpha", "1.2.3", -1),
        ("1.2.3", "1.2.3-alpha", 1),
        ("1.2.3-alpha.1", "1.2.3-alpha.2", -1),
        ("1.2.3-alpha.2", "1.2.3-alpha.10", -1),
        ("1.2.3-alpha", "1.2.3-alpha.1", -1),
        ("1.2.3-alpha.1", "1.2.3-alpha.beta", -1),
        ("1.2.3-alpha.beta", "1.2.3-alpha.1", 1),
    ],
)
def test_compare_versions(left: str, right: str, expected: int) -> None:
    assert (
        go_release.compare_versions(Version.parse(left), Version.parse(right))
        == expected
    )


@pytest.mark.parametrize(
    ("tag", "prefix", "expected"),
    [
        ("v1.2.3", "", "1.2.3"),
        ("sub/v1.2.3", "sub/", "1.2.3"),
        ("v1.2.3+build", "", "1.2.3+build"),
        ("not-a-version", "", None),
        ("sub/not-a-version", "sub/", None),
        ("v1.2.3", "sub/", None),
    ],
)
def test_version_from_tag(
    tag: str,
    prefix: str,
    expected: str | None,
) -> None:
    version = go_release.version_from_tag(tag, prefix)
    assert (str(version) if version else None) == expected


def test_version_from_tag_can_skip_prefix() -> None:
    version = go_release.version_from_tag("v1.2.3", "sub/", require_prefix=False)
    assert version is not None
    assert str(version) == "1.2.3"


def test_tag_pattern_and_regex_default() -> None:
    pattern, regex = go_release.tag_pattern_and_regex("sub/", None)
    assert pattern == "sub/v[0-9]*"
    assert regex is None


def test_tag_pattern_and_regex_custom() -> None:
    pattern, regex = go_release.tag_pattern_and_regex(
        "sub/",
        "{{prefix}}release-{{version}}",
    )
    assert pattern == "sub/release-*"
    assert regex is not None
    match = regex.fullmatch("sub/release-1.2.3-rc.1")
    assert match is not None
    assert match.group("version") == "1.2.3-rc.1"


@pytest.mark.parametrize(
    "template",
    ["release", "{{version}}-{{prev_version}}", ""],
)
def test_tag_pattern_requires_one_version_placeholder(template: str) -> None:
    with pytest.raises(go_release.ReleaseError):
        go_release.tag_pattern_and_regex("", template)


def test_render_placeholders() -> None:
    assert (
        go_release.render_placeholders(
            "{{prefix}}v{{version}}",
            {"prefix": "sub/", "version": "1.2.3"},
        )
        == "sub/v1.2.3"
    )
    assert go_release.render_placeholders("{{unknown}}", {}) == "{{unknown}}"


def test_render_placeholders_is_not_recursive() -> None:
    assert (
        go_release.render_placeholders(
            "{{tag_name}}",
            {"tag_name": "{{version}}", "version": "1.0.0"},
        )
        == "{{version}}"
    )


@pytest.mark.parametrize(
    ("specs", "branch", "should_raise"),
    [
        ([], "main", False),
        (["main"], "main", False),
        (["dev"], "main", True),
        (["!main"], "main", True),
        (["!main"], "dev", False),
        (["main,dev"], "dev", False),
        (["main,!main"], "main", True),
        (["release/*"], "release/1.2", False),
    ],
)
def test_check_allowed_branch(
    specs: list[str],
    branch: str,
    should_raise: bool,
) -> None:
    if should_raise:
        with pytest.raises(go_release.ReleaseError):
            go_release._check_allowed_branch(branch, specs)
    else:
        go_release._check_allowed_branch(branch, specs)


def test_next_version_metadata() -> None:
    current = Version.parse("1.2.3")
    assert str(go_release._next_version(current, "patch", "build.5")) == "1.2.4+build.5"
    assert str(go_release._next_version(current, "v2.0.0", None)) == "2.0.0"
    assert str(go_release._next_version(current, "v2.0.0+foo", None)) == "2.0.0+foo"
    assert (
        str(go_release._next_version(current, "v2.0.0+foo", "bar.1")) == "2.0.0+bar.1"
    )


def test_next_version_rejects_metadata_with_spaces() -> None:
    with pytest.raises(go_release.ReleaseError):
        go_release._next_version(Version.parse("1.2.3"), "patch", "bad metadata")


def test_next_version_must_increase() -> None:
    with pytest.raises(go_release.ReleaseError):
        go_release._next_version(Version.parse("1.2.3"), "v1.2.3", None)
    with pytest.raises(go_release.ReleaseError):
        go_release._next_version(Version.parse("1.2.3"), "v1.2.2", None)


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git in *repo* and return the completed process."""
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Create a work repo with a bare remote and one commit."""
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"

    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(work)], check=True)

    run_git(work, "config", "user.email", "test@example.com")
    run_git(work, "config", "user.name", "Test")
    run_git(work, "config", "commit.gpgsign", "false")
    run_git(work, "config", "tag.gpgsign", "false")
    run_git(work, "remote", "add", "origin", str(remote))

    (work / "go.mod").write_text("module example.com/test\n\ngo 1.22\n")
    run_git(work, "add", "go.mod")
    run_git(work, "commit", "-q", "-m", "initial")
    run_git(work, "push", "-q", "-u", "origin", "HEAD")
    return work


def test_dry_run_does_not_tag(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(repo)
    assert go_release.main([]) == 0
    assert run_git(repo, "tag", "--list").stdout == ""

    output = capsys.readouterr().out
    assert "New tag:          v0.0.1" in output
    assert "Dry run: no tag was created" in output


def test_execute_creates_and_pushes_tag(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    assert go_release.main(["-x", "--no-confirm", "-q"]) == 0

    assert run_git(repo, "tag", "--list").stdout.strip() == "v0.0.1"
    remote_tags = subprocess.run(
        ["git", "--git-dir", str(repo.parent / "remote.git"), "tag", "--list"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    assert remote_tags.strip() == "v0.0.1"

    contents = run_git(repo, "tag", "-l", "--format=%(contents)", "v0.0.1").stdout
    assert "Release v0.0.1" in contents


def test_release_levels(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    for level, expected in [
        ("patch", "v0.0.1"),
        ("alpha", "v0.0.2-alpha.1"),
        ("alpha", "v0.0.2-alpha.2"),
        ("beta", "v0.0.2-beta.1"),
        ("patch", "v0.0.2"),
        ("minor", "v0.1.0"),
        ("major", "v1.0.0"),
        ("v2.0.0", "v2.0.0"),
    ]:
        assert go_release.main(["-x", "--no-confirm", "-q", level]) == 0
        tags = run_git(repo, "tag", "--list").stdout.splitlines()
        assert expected in tags


def test_tag_prefix(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    args = ["-x", "--no-confirm", "-q", "--tag-prefix", "sub/", "patch"]
    assert go_release.main(args) == 0
    assert run_git(repo, "tag", "--list").stdout.strip() == "sub/v0.0.1"
    assert go_release.main(args) == 0
    assert sorted(run_git(repo, "tag", "--list").stdout.splitlines()) == [
        "sub/v0.0.1",
        "sub/v0.0.2",
    ]


def test_tag_name_and_message(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    assert (
        go_release.main(
            [
                "-x",
                "--no-confirm",
                "-q",
                "--tag-name",
                "release-{{version}}",
                "--tag-message",
                "{{tag_name}} on {{date}}",
            ]
        )
        == 0
    )
    assert run_git(repo, "tag", "--list").stdout.strip() == "release-0.0.1"
    contents = run_git(
        repo,
        "tag",
        "-l",
        "--format=%(contents)",
        "release-0.0.1",
    ).stdout
    assert "release-0.0.1 on " in contents

    assert (
        go_release.main(
            [
                "-x",
                "--no-confirm",
                "-q",
                "--tag-name",
                "release-{{version}}",
            ]
        )
        == 0
    )
    assert sorted(run_git(repo, "tag", "--list").stdout.splitlines()) == [
        "release-0.0.1",
        "release-0.0.2",
    ]


def test_no_tag_and_no_push(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(repo)
    assert go_release.main(["-x", "--no-confirm", "--no-tag", "--no-push"]) == 0
    assert run_git(repo, "tag", "--list").stdout == ""
    assert "Not pushing (--no-push)." in capsys.readouterr().out


def test_no_push_leaves_tag_local(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(repo)
    assert go_release.main(["-x", "--no-confirm", "--no-push"]) == 0
    assert run_git(repo, "tag", "--list").stdout.strip() == "v0.0.1"
    assert "Created v0.0.1 locally" in capsys.readouterr().out


def test_dirty_worktree(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(repo)
    (repo / "go.mod").write_text("module example.com/changed\n\ngo 1.22\n")

    assert go_release.main(["-x", "--no-confirm"]) == 1
    assert "working tree has uncommitted changes" in capsys.readouterr().err
    assert run_git(repo, "tag", "--list").stdout == ""

    assert go_release.main(["-x", "--no-confirm", "-q", "--allow-dirty"]) == 0
    assert run_git(repo, "tag", "--list").stdout.strip() == "v0.0.1"


def test_detached_head_is_rejected(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_git(repo, "checkout", "-q", "--detach", "HEAD")
    monkeypatch.chdir(repo)

    assert go_release.main(["-x", "--no-confirm"]) == 1
    assert "detached HEAD" in capsys.readouterr().err


def test_allow_branch(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    assert go_release.main(["-x", "--no-confirm", "-q", "--allow-branch", "main"]) == 0
    assert go_release.main(["-x", "--no-confirm", "-q", "--allow-branch", "!main"]) == 1


def test_metadata(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    assert go_release.main(["-x", "--no-confirm", "-q", "-m", "build.5"]) == 0
    assert run_git(repo, "tag", "--list").stdout.strip() == "v0.0.1+build.5"


def test_explicit_version_must_increase(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(repo)
    run_git(repo, "tag", "-a", "-m", "old", "v1.2.3")

    assert go_release.main(["-x", "--no-confirm", "v1.2.3"]) == 1
    assert go_release.main(["-x", "--no-confirm", "v1.2.2"]) == 1
    assert run_git(repo, "tag", "--list").stdout.strip() == "v1.2.3"
