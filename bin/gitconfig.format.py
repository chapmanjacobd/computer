#!/usr/bin/env python3
"""Normalize git-config-syntax files (INI-like, not TOML).

Canonical form: [section "subsection"] headers with lowercase section/key
names, one tab of indentation, "key = value" spacing, no trailing whitespace.
Values and inline comments are preserved verbatim. Semantics are verified by
comparing `git config --file <f> --list --null` before and after.

Usage:
    gitconfig_fmt.py [--check] FILE...
"""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HEADER_RE = re.compile(r"^(?P<indent>\s*)\[(?P<inner>.*)\](?P<comment>\s*[#;].*)?$")
QUOTED_RE = re.compile(r'^(?P<name>[^\s"]+)\s*"(?P<sub>(?:[^"\\]|\\.)*)"$')
KEYVAL_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<key>[^=\s][^=]*?)[ \t]*=[ \t]*(?P<value>.*)$")
BARE_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<key>[^#;\s][^#;]*?)[ \t]*$")


def normalize_header(line: str) -> str:
    m = HEADER_RE.match(line)
    if not m:
        raise ValueError(f"unparsable section header: {line!r}")

    inner = m["inner"].strip()
    q = QUOTED_RE.match(inner)
    if q:
        header = f'[{q["name"].lower()} "{q["sub"]}"]'
    elif "." in inner:
        name, sub = inner.split(".", 1)
        header = f'[{name.lower()} "{sub}"]'
    else:
        header = f"[{inner.lower()}]"
    return header + (m["comment"] or "")


def format_text(text: str) -> str:
    out: list[str] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            if out and out[-1] != "":
                out.append("")
            continue

        if stripped.startswith(("#", ";")):
            out.append(line)
            continue

        if stripped.startswith("["):
            out.append(normalize_header(stripped))
            continue

        m = KEYVAL_RE.match(line)
        if m:
            key = m["key"].strip().lower()
            value = m["value"]
            out.append(f"\t{key} = {value}" if value else f"\t{key} =")
            continue

        m = BARE_RE.match(line)
        if m:
            out.append(f'\t{m["key"].strip().lower()}')
            continue

        raise ValueError(f"{lineno}: unparsable line: {raw!r}")

    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"


def semantic_dump(path: Path) -> bytes:
    return subprocess.run(
        ["git", "config", "--file", str(path), "--list", "--null"],
        check=True,
        capture_output=True,
    ).stdout


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report differences, do not write")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)

    exit_code = 0
    for path in args.files:
        original = path.read_text()
        try:
            formatted = format_text(original)
        except ValueError as exc:
            print(f"{path}: parse error: {exc}", file=sys.stderr)
            return 2

        if formatted == original:
            continue

        with tempfile.NamedTemporaryFile("w", suffix=".cfg", delete=True) as tmp:
            tmp.write(formatted)
            tmp.flush()
            if semantic_dump(path) != semantic_dump(Path(tmp.name)):
                print(f"{path}: REFUSING to format: git config semantics changed", file=sys.stderr)
                return 2

        if args.check:
            exit_code = 1
            sys.stdout.writelines(
                difflib.unified_diff(
                    original.splitlines(keepends=True),
                    formatted.splitlines(keepends=True),
                    fromfile=str(path),
                    tofile=str(path),
                )
            )
        else:
            path.write_text(formatted)
            print(f"formatted {path}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
