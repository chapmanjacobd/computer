#!/usr/bin/env pytest
# SPDX-License-Identifier: WTFPL

"""Tests for cmd.info."""

import doctest
import importlib.machinery
import importlib.util
import io
import os
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).with_name("cmd.info")
_LOADER = importlib.machinery.SourceFileLoader("cmd_info", str(_SCRIPT))
_SPEC = importlib.util.spec_from_loader("cmd_info", _LOADER)
assert _SPEC is not None
ci = importlib.util.module_from_spec(_SPEC)
sys.modules["cmd_info"] = ci
_LOADER.exec_module(ci)


def test_doctests() -> None:
    failures, _ = doctest.testmod(ci)
    assert failures == 0


def make_exec(path: Path, body: str = "#!/bin/sh\necho hello\n") -> Path:
    """Create an executable text file."""
    path.write_text(body)
    path.chmod(0o755)
    return path


def make_binary(path: Path) -> Path:
    """Create an executable file that looks binary to ``file``."""
    path.write_bytes(b"\x7fELF" + b"\x00" * 64)
    path.chmod(0o755)
    return path


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0", "0 B"),
        ("1", "1 B"),
        ("1023", "1023 B"),
        ("1024", "1.0 KiB"),
        ("1536", "1.5 KiB"),
        ("1048576", "1.0 MiB"),
        ("1073741824", "1.0 GiB"),
    ],
)
def test_human_size(value: str, expected: str) -> None:
    assert ci.human_size(int(value)) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("plain", "plain"),
        ("\x1b[31mred\x1b[0m", "red"),
        ("bell\x07", "bell"),
        ("\x1b]0;title\x07kept", "kept"),
    ],
)
def test_clean_text(text: str, expected: str) -> None:
    assert ci.clean_text(text) == expected


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("", ""),
        ("#!/bin/sh", "sh"),
        ("#!/bin/sh -e", "sh -e"),
        ("#!/usr/bin/env bash", "bash"),
        ("#!/usr/bin/env -S uv run --script", "uv run --script"),
        ("#!/usr/bin/env FOO=bar python3 -u", "python3 -u"),
        ("#!/usr/bin/python3", "python3"),
        ("just text", ""),
    ],
)
def test_parse_shebang(line: str, expected: str) -> None:
    assert ci.parse_shebang(line) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"", True),
        (b"#!/bin/sh\necho hi\n", True),
        (b"\x7fELF\x00\x00", False),
        (b"caf\xc3\xa9", True),
        (b"\xff\xfe\x00\x00", False),
    ],
)
def test_is_probably_text(data: bytes, expected: bool) -> None:
    assert ci.is_probably_text(data) is expected


def test_find_matches_preserves_path_order(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    make_exec(first / "tool", "#!/bin/sh\necho first\n")
    make_exec(second / "tool", "#!/bin/sh\necho second\n")

    matches = ci.find_matches("tool", f"{first}:{second}")

    assert matches == [str(first / "tool"), str(second / "tool")]


def test_find_matches_skips_non_executable_files_and_directories(
    tmp_path: Path,
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "tool").write_text("not executable")
    (bin_dir / "tool").chmod(0o644)
    (bin_dir / "other").mkdir()

    assert ci.find_matches("tool", str(bin_dir)) == []
    assert ci.find_matches("other", str(bin_dir)) == []


def test_find_matches_dedupes_the_same_real_file(tmp_path: Path) -> None:
    real = tmp_path / "real"
    alias = tmp_path / "alias"
    real.mkdir()
    alias.mkdir()
    make_exec(real / "tool")
    (alias / "tool").symlink_to(real / "tool")

    assert ci.find_matches("tool", f"{real}:{alias}") == [str(real / "tool")]


def test_find_matches_accepts_an_explicit_relative_path(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    make_exec(tmp_path / "tool")

    assert ci.find_matches("./tool", "") == [str(tmp_path / "tool")]


def test_find_matches_accepts_an_explicit_non_executable_file(
    tmp_path: Path,
) -> None:
    target = tmp_path / "notes.txt"
    target.write_text("read me\n")

    assert ci.find_matches(str(target), "") == [str(target)]


def test_read_source_truncates(tmp_path: Path) -> None:
    target = tmp_path / "script"
    target.write_text("one\ntwo\nthree\n")

    lines, truncated = ci.read_source(target, max_lines=2)

    assert lines == ("one", "two")
    assert truncated is True


def test_read_source_full(tmp_path: Path) -> None:
    target = tmp_path / "script"
    target.write_text("one\ntwo\nthree\n")

    lines, truncated = ci.read_source(target, max_lines=2, full=True)

    assert lines == ("one", "two", "three")
    assert truncated is False


def test_parse_go_build_info_with_module(tmp_path: Path) -> None:
    output = (
        "/home/xk/bin/centroidify: go1.26.1\n"
        "\tpath\tgithub.com/chapmanjacobd/computer/bin/centroidify\n"
        "\tmod\tgithub.com/chapmanjacobd/computer/bin/centroidify\t(devel)\t\n"
        "\tbuild\t-buildmode=exe\n"
    )

    assert (
        ci.parse_go_build_info(output)
        == "go1.26.1 · github.com/chapmanjacobd/computer/bin/centroidify (devel)"
    )


def test_parse_go_build_info_without_module() -> None:
    output = (
        "/home/xk/bin/anagram: go1.25.1\n"
        "\tpath\tcommand-line-arguments\n"
        "\tbuild\t-buildmode=exe\n"
    )

    assert ci.parse_go_build_info(output) == "go1.25.1"


def test_parse_go_build_info_rejects_errors() -> None:
    assert ci.parse_go_build_info("not a Go executable") == ""


@pytest.mark.parametrize(
    ("is_text", "is_regular", "is_setuid", "is_setgid", "world_writable", "expected"),
    [
        (False, True, False, False, False, True),
        (True, True, False, False, False, False),
        (False, False, False, False, False, False),
        (False, True, True, False, False, False),
        (False, True, False, True, False, False),
        (False, True, False, False, True, False),
    ],
)
def test_should_probe_version(
    is_text: bool,
    is_regular: bool,
    is_setuid: bool,
    is_setgid: bool,
    world_writable: bool,
    expected: bool,
) -> None:
    facts = ci.FileFacts(
        path="/tmp/tool",
        real_path="/tmp/tool",
        link_target="",
        description="ELF",
        size=1,
        mode=0o755,
        is_text=is_text,
        is_regular=is_regular,
        is_setuid=is_setuid,
        is_setgid=is_setgid,
        is_world_writable=world_writable,
        shebang="",
        interpreter="",
    )

    assert ci.should_probe_version(facts) is expected


def test_probe_version_uses_first_line_and_filters_terminal_sequences(
    tmp_path: Path,
) -> None:
    target = make_exec(
        tmp_path / "demo",
        "#!/bin/sh\nprintf '\\033[31mdemo 1.2\\033[0m\\nsecond line\\n'\n",
    )

    assert ci.probe_version(str(target), timeout=1) == "demo 1.2"


def test_probe_version_accepts_stderr_version_output(tmp_path: Path) -> None:
    target = make_exec(
        tmp_path / "demo",
        "#!/bin/sh\necho 'demo 2.0' >&2\n",
    )

    assert ci.probe_version(str(target), timeout=1) == "demo 2.0"


def test_probe_version_rejects_usage_text(tmp_path: Path) -> None:
    target = make_exec(
        tmp_path / "demo",
        "#!/bin/sh\necho 'Usage: demo [options]'\n",
    )

    assert ci.probe_version(str(target), timeout=1) == ""


def test_probe_version_kills_a_hanging_command(tmp_path: Path) -> None:
    target = make_exec(tmp_path / "demo", "#!/bin/sh\nsleep 10\n")

    assert ci.probe_version(str(target), timeout=0.2) == ""


def test_origin_info_labels_user_files(tmp_path: Path) -> None:
    target = make_exec(tmp_path / "tool")

    origin = ci.origin_info(str(target), home=str(tmp_path))

    assert origin.kind == "user"
    assert origin.label == "user file"


@pytest.mark.parametrize(
    ("relative", "kind", "label"),
    [
        (".local/share/uv/tools/demo/bin/demo", "uv", "uv"),
        (".cargo/bin/demo", "cargo", "cargo"),
        (".local/share/cargo/bin/demo", "cargo", "cargo"),
        (".local/bin/demo", "user-install", "user install"),
    ],
)
def test_origin_info_labels_install_styles(
    tmp_path: Path, relative: str, kind: str, label: str
) -> None:
    origin = ci.origin_info(str(tmp_path / relative), home=str(tmp_path))

    assert origin.kind == kind
    assert origin.label == label


@pytest.mark.parametrize(
    ("output", "expected"),
    [
        ("bash: /data/data/com.termux/files/usr/bin/bash\n", "bash"),
        ("libc6:amd64: /data/data/com.termux/files/usr/lib/libc.so\n", "libc6:amd64"),
        ("pkg1, pkg2: /data/data/com.termux/files/usr/bin/tool\n", "pkg1"),
        ("diversion by foo from: /old\ndiversion by foo to: /new\n", ""),
        ("no owner\n", ""),
        ("", ""),
    ],
)
def test_parse_dpkg_owner(output: str, expected: str) -> None:
    assert ci.parse_dpkg_owner(output) == expected


def test_dpkg_info_reads_owner_and_version(tmp_path: Path) -> None:
    stub = make_exec(
        tmp_path / "dpkg-query",
        """#!/bin/sh
case "$1" in
    -S) printf 'bash: %s\\n' "$2" ;;
    -W) printf '5.2.37\\n' ;;
esac
""",
    )

    assert ci.dpkg_info("/data/data/com.termux/files/usr/bin/bash", str(stub)) == (
        "bash",
        "5.2.37",
    )


def test_dpkg_info_returns_empty_when_unowned(tmp_path: Path) -> None:
    stub = make_exec(tmp_path / "dpkg-query", "#!/bin/sh\nexit 1\n")

    assert ci.dpkg_info("/data/data/com.termux/files/usr/bin/tool", str(stub)) == (
        "",
        "",
    )


@pytest.mark.parametrize(
    ("environment", "expected"),
    [
        ({}, ""),
        ({"PREFIX": "/usr"}, ""),
        (
            {"PREFIX": "/data/data/com.termux/files/usr"},
            "/data/data/com.termux/files/usr",
        ),
        ({"PREFIX": "/custom", "TERMUX_VERSION": "0.118"}, "/custom"),
    ],
)
def test_termux_prefix(environment: dict[str, str], expected: str) -> None:
    assert ci.termux_prefix(environment) == expected


def test_origin_info_uses_dpkg_for_the_termux_prefix(tmp_path: Path) -> None:
    prefix = tmp_path / "termux" / "usr"
    stub = make_exec(
        tmp_path / "dpkg-query",
        """#!/bin/sh
case "$1" in
    -S) printf 'bash: %s\\n' "$2" ;;
    -W) printf '5.2.37\\n' ;;
esac
""",
    )

    origin = ci.origin_info(
        str(prefix / "bin" / "bash"),
        home=str(tmp_path / "home"),
        prefix=str(prefix),
        dpkg_query=str(stub),
    )

    assert origin.kind == "dpkg"
    assert origin.label == "bash 5.2.37"


def test_origin_info_labels_unowned_termux_files(tmp_path: Path) -> None:
    prefix = tmp_path / "termux" / "usr"
    stub = make_exec(tmp_path / "dpkg-query", "#!/bin/sh\nexit 1\n")

    origin = ci.origin_info(
        str(prefix / "bin" / "local-tool"),
        home=str(tmp_path / "home"),
        prefix=str(prefix),
        dpkg_query=str(stub),
    )

    assert origin.kind == "termux"
    assert origin.label == "termux prefix"


def test_origin_info_uses_rpm(monkeypatch) -> None:
    monkeypatch.setattr(ci, "rpm_info", lambda *args, **kwargs: ("coreutils", "9.7-1"))

    origin = ci.origin_info("/usr/bin/ls", home="/home/nobody")

    assert origin.kind == "rpm"
    assert origin.label == "coreutils 9.7-1"


def test_origin_info_can_be_disabled() -> None:
    origin = ci.origin_info("/usr/bin/ls", home="/home/nobody", enabled=False)

    assert origin.kind == ""
    assert origin.label == ""


def test_file_facts_follows_a_symlink(tmp_path: Path) -> None:
    target = make_exec(tmp_path / "tool")
    link = tmp_path / "alias"
    link.symlink_to("tool")

    facts = ci.file_facts(str(link))

    assert facts.path == str(link)
    assert facts.link_target == "tool"
    assert facts.real_path == str(target)
    assert facts.is_text is True


@pytest.mark.skipif(os.geteuid() == 0, reason="root can read everything")
def test_file_facts_does_not_treat_an_unreadable_file_as_text(
    tmp_path: Path,
) -> None:
    target = tmp_path / "secret"
    target.write_bytes(b"\x7fELF" + b"\x00" * 64)
    target.chmod(0o000)

    facts = ci.file_facts(str(target))

    assert facts.is_text is False


def test_fish_info_reads_a_function(tmp_path: Path) -> None:
    fake_fish = make_exec(
        tmp_path / "fish",
        """#!/bin/sh
case "$2" in
    *"builtin type -t"*) echo function ;;
    *"functions --details"*) echo /tmp/ls.fish ;;
    *"functions --"*)
        printf '%s\\n' '# Defined in /tmp/ls.fish @ line 2' 'function ls' '    echo hi' 'end'
        ;;
esac
""",
    )

    info = ci.fish_info("ls", fish=str(fake_fish))

    assert info is not None
    assert info.kind == "function"
    assert info.details == "/tmp/ls.fish"
    assert info.source_lines == ("function ls", "    echo hi", "end")


def test_fish_info_detects_a_builtin(tmp_path: Path) -> None:
    fake_fish = make_exec(
        tmp_path / "fish",
        """#!/bin/sh
case "$2" in
    *"builtin type -t"*) echo builtin ;;
esac
""",
    )

    info = ci.fish_info("type", fish=str(fake_fish))

    assert info is not None
    assert info.kind == "builtin"
    assert info.source_lines == ()


def test_inspect_reads_a_script(tmp_path: Path) -> None:
    target = make_exec(tmp_path / "hello", "#!/bin/sh\necho hello\n")

    infos = ci.inspect(
        "hello",
        path_value=str(tmp_path),
        home=str(tmp_path),
        fish="",
    )

    assert len(infos) == 1
    info = infos[0]
    assert info.kind == "file"
    assert info.path == str(target)
    assert info.interpreter == "sh"
    assert info.source_lines == ("#!/bin/sh", "echo hello")
    assert info.origin == "user file"


def test_inspect_does_not_execute_scripts(tmp_path: Path) -> None:
    marker = tmp_path / "ran"
    target = make_exec(
        tmp_path / "hello",
        f"#!/bin/sh\ntouch {marker}\necho hello\n",
    )

    infos = ci.inspect(
        "hello",
        path_value=str(tmp_path),
        home=str(tmp_path),
        fish="",
    )

    assert infos[0].version == ""
    assert not marker.exists()
    assert target.exists()


def test_inspect_uses_version_probe_for_binaries(tmp_path: Path, monkeypatch) -> None:
    target = make_binary(tmp_path / "tool")
    monkeypatch.setattr(ci, "probe_version", lambda *args, **kwargs: "tool 1.0")
    monkeypatch.setattr(ci, "go_version", lambda *args, **kwargs: "")

    infos = ci.inspect(
        "tool",
        path_value=str(tmp_path),
        home=str(tmp_path),
        fish="",
    )

    assert infos[0].version == "tool 1.0"
    assert infos[0].source_lines == ()
    assert target.exists()


def test_inspect_can_skip_versions_and_source(tmp_path: Path) -> None:
    make_exec(tmp_path / "hello", "#!/bin/sh\necho hello\n")

    infos = ci.inspect(
        "hello",
        path_value=str(tmp_path),
        home=str(tmp_path),
        fish="",
        versions=False,
        source=False,
    )

    assert infos[0].version == ""
    assert infos[0].source_lines == ()


def test_inspect_finds_all_matches(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    make_exec(first / "tool", "#!/bin/sh\necho first\n")
    make_exec(second / "tool", "#!/bin/sh\necho second\n")
    path_value = f"{first}:{second}"

    infos = ci.inspect(
        "tool",
        path_value=path_value,
        home=str(tmp_path),
        fish="",
        all_matches=True,
    )

    assert [info.path for info in infos] == [
        str(first / "tool"),
        str(second / "tool"),
    ]


def test_inspect_reports_missing() -> None:
    infos = ci.inspect("definitely-not-a-command", path_value="", fish="")

    assert infos[0].kind == "missing"


def test_render_info_for_a_script() -> None:
    info = ci.CommandInfo(
        name="hello",
        kind="file",
        path="/home/xk/bin/hello",
        real_path="/home/xk/bin/hello",
        description="Bourne-Again shell script, ASCII text executable",
        size=21,
        interpreter="sh",
        origin="user file",
        occurrences=("/home/xk/bin/hello", "/usr/local/bin/hello"),
        source_lines=("#!/bin/sh", "echo hello"),
    )

    text = ci.render_info(info)

    assert text.startswith("hello\n")
    assert "path" in text
    assert "/home/xk/bin/hello" in text
    assert "origin" in text
    assert "interpreter" in text
    assert "also on PATH" in text
    assert "echo hello" in text


@pytest.mark.parametrize("kind", ["rpm", "dpkg"])
def test_render_info_calls_a_package_owner_a_package(kind: str) -> None:
    info = ci.CommandInfo(
        name="ls",
        kind="file",
        path="/usr/bin/ls",
        description="ELF",
        size=1,
        origin="coreutils 9.7-1",
        origin_kind=kind,
    )

    text = ci.render_info(info)

    assert "package" in text
    assert "coreutils 9.7-1" in text


def test_render_info_for_a_function() -> None:
    info = ci.CommandInfo(
        name="ls",
        kind="function",
        details="/home/xk/.config/fish/functions/ls.fish",
        source_lines=("function ls", "end"),
    )

    text = ci.render_info(info)

    assert "fish function" in text
    assert "/home/xk/.config/fish/functions/ls.fish" in text
    assert "function ls" in text


def test_render_info_marks_truncated_source() -> None:
    info = ci.CommandInfo(
        name="hello",
        kind="file",
        path="/home/xk/bin/hello",
        description="Python script",
        size=10,
        source_lines=("one", "two"),
        source_truncated=True,
    )

    text = ci.render_info(info)

    assert "more lines" in text
    assert "--full" in text


def test_main_which_mode_and_exit_status(tmp_path: Path) -> None:
    target = make_exec(tmp_path / "hello", "#!/bin/sh\necho hello\n")
    out = io.StringIO()
    err = io.StringIO()

    status = ci.main(
        ["--which", "hello"],
        path_value=str(tmp_path),
        home=str(tmp_path),
        out=out,
        err=err,
    )

    assert status == 0
    assert str(target) in out.getvalue()
    assert "echo hello" in out.getvalue()


def test_main_reports_missing_commands(tmp_path: Path) -> None:
    out = io.StringIO()
    err = io.StringIO()

    status = ci.main(
        ["--which", "no-such-command"],
        path_value=str(tmp_path),
        home=str(tmp_path),
        out=out,
        err=err,
    )

    assert status == 1
    assert "no-such-command: not found" in err.getvalue()


def test_main_all_and_no_source(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    make_exec(first / "tool", "#!/bin/sh\necho first\n")
    make_exec(second / "tool", "#!/bin/sh\necho second\n")
    out = io.StringIO()

    status = ci.main(
        ["--which", "--all", "--no-source", "tool"],
        path_value=f"{first}:{second}",
        home=str(tmp_path),
        out=out,
        err=io.StringIO(),
    )

    assert status == 0
    assert str(first / "tool") in out.getvalue()
    assert str(second / "tool") in out.getvalue()
    assert "echo first" not in out.getvalue()
