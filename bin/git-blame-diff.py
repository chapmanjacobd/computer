#!/usr/bin/env python3
"""Render diff hunks with blame metadata for old and current lines."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path


HUNK_RE = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? "
    r"\+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)


def run_git(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        encoding="utf-8",
        errors="surrogateescape",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def blame_arguments(
    revision: str | None,
    path: str,
    contents: str | None = None,
    porcelain: bool = True,
) -> list[str]:
    arguments = ["blame"]
    if porcelain:
        arguments.append("--line-porcelain")
    if contents is not None:
        arguments.extend(["--contents", contents])
    if revision is not None:
        arguments.append(revision)
    arguments.extend(["--", path])
    return arguments


def blame_lines(
    revision: str | None,
    path: str,
    contents: str | None = None,
) -> dict[int, tuple[str, str]]:
    result = run_git(blame_arguments(revision, path, contents))
    if result.returncode != 0:
        return {}

    blamed: dict[int, tuple[str, str]] = {}
    lines = result.stdout.splitlines()
    index = 0
    while index < len(lines):
        header = lines[index].split()
        if len(header) < 3:
            index += 1
            continue

        try:
            final_line = int(header[2])
        except ValueError:
            index += 1
            continue

        commit = header[0][:9]
        author = ""
        index += 1
        content = None
        while index < len(lines):
            line = lines[index]
            if line.startswith("\t"):
                content = line[1:]
                break
            if line.startswith("author "):
                author = line[7:]
            index += 1

        if content is not None:
            metadata = f"[{commit} {author}]".strip()
            blamed[final_line] = (metadata, content)
        index += 1

    return blamed


def metadata(blamed: dict[int, tuple[str, str]], line_number: int) -> str:
    return blamed.get(line_number, ("[unknown]", ""))[0]


def render_diff(
    diff: str,
    base_blame: dict[int, tuple[str, str]],
    current_blame: dict[int, tuple[str, str]],
) -> bool:
    lines = diff.splitlines()
    rendered_hunk = False
    index = 0

    while index < len(lines):
        line = lines[index]
        hunk = HUNK_RE.match(line)
        if not hunk:
            if line.startswith(
                (
                    "diff --git ",
                    "new file mode ",
                    "deleted file mode ",
                    "similarity index ",
                    "rename from ",
                    "rename to ",
                    "--- ",
                    "+++ ",
                    "Binary files ",
                )
            ):
                print(line)
            index += 1
            continue

        rendered_hunk = True
        print(line)
        old_line = int(hunk.group("old_start"))
        new_line = int(hunk.group("new_start"))
        index += 1

        while index < len(lines):
            diff_line = lines[index]
            if HUNK_RE.match(diff_line) or diff_line.startswith("diff --git "):
                break
            if diff_line.startswith("\\"):
                print(diff_line)
                index += 1
                continue
            if not diff_line or diff_line[0] not in " +-":
                index += 1
                continue

            kind = diff_line[0]
            content = diff_line[1:]
            if kind == "-":
                line_metadata = metadata(base_blame, old_line)
                old_line += 1
            elif kind == "+":
                line_metadata = metadata(current_blame, new_line)
                new_line += 1
            else:
                line_metadata = metadata(current_blame, new_line)
                old_line += 1
                new_line += 1

            print(f"{kind}{line_metadata} {content}")
            index += 1

    return rendered_hunk


def changed_paths(revision: str, staged: bool) -> list[str] | None:
    arguments = ["diff"]
    if staged:
        arguments.append("--cached")
    arguments.extend(
        [
            "--name-only",
            "-z",
            "--diff-filter=ACMRTUXBD",
            revision,
            "--",
        ]
    )
    result = run_git(arguments)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return None
    return [path for path in result.stdout.split("\0") if path]


def is_revision(value: str) -> bool:
    return run_git(["rev-parse", "--verify", f"{value}^{{commit}}"]).returncode == 0


def is_tracked_path(value: str) -> bool:
    if Path(value).exists():
        return True
    result = run_git(["ls-tree", "-r", "--name-only", "HEAD", "--", value])
    return result.returncode == 0 and bool(result.stdout.strip())


def render_path(revision: str, path: str, staged: bool) -> bool:
    diff_arguments = ["diff"]
    if staged:
        diff_arguments.append("--cached")
    diff_arguments.extend(
        [
            "--no-ext-diff",
            "--no-textconv",
            "--no-color",
            "--unified=3",
            revision,
            "--",
            path,
        ]
    )
    result = run_git(diff_arguments)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return False

    if staged:
        index_contents = subprocess.run(
            ["git", "show", f":{path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if index_contents.returncode == 0:
            with tempfile.NamedTemporaryFile() as contents:
                contents.write(index_contents.stdout)
                contents.flush()
                if not result.stdout:
                    blame = run_git(
                        blame_arguments(revision, path, contents.name, porcelain=False)
                    )
                    if blame.returncode != 0:
                        sys.stderr.write(blame.stderr)
                        return False
                    print(f"==> {path} <==")
                    sys.stdout.write(blame.stdout)
                    return True
                base_blame = blame_lines(revision, path)
                current_blame = blame_lines(revision, path, contents.name)
                if not render_diff(result.stdout, base_blame, current_blame):
                    sys.stdout.write(result.stdout)
                return True
        if not result.stdout:
            sys.stderr.buffer.write(index_contents.stderr)
            return False

    if not result.stdout:
        blame = run_git(blame_arguments(None, path, porcelain=False))
        if blame.returncode != 0:
            sys.stderr.write(blame.stderr)
            return False
        print(f"==> {path} <==")
        sys.stdout.write(blame.stdout)
        return True

    base_blame = blame_lines(revision, path)
    current_blame = blame_lines(None, path)
    if not render_diff(result.stdout, base_blame, current_blame):
        sys.stdout.write(result.stdout)
    return True


def main() -> int:
    arguments = sys.argv[1:]
    staged = "--staged" in arguments
    arguments = [argument for argument in arguments if argument != "--staged"]
    revision = "HEAD"
    paths: list[str] = []

    if arguments:
        if arguments[0] == "--":
            paths = arguments[1:]
        elif is_revision(arguments[0]):
            revision = arguments[0]
            paths = arguments[1:]
        elif is_tracked_path(arguments[0]):
            paths = arguments
        else:
            revision = arguments[0]
            paths = arguments[1:]
            if paths and paths[0] == "--":
                paths = paths[1:]

    if not paths:
        selected_paths = changed_paths(revision, staged)
        if selected_paths is None:
            return 1
        paths = selected_paths

    if not paths:
        print(f"No blameable files changed relative to {revision}", file=sys.stderr)
        return 0

    for path in paths:
        if not render_path(revision, path, staged):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
