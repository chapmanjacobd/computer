#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["tabulate"]
# ///
# SPDX-License-Identifier: WTFPL

"""Report executable name collisions across $PATH.

Every directory in ``$PATH`` is scanned for executable files. Commands found
in exactly one place are listed grouped by that directory; commands whose name
appears in several places are reported one table per name, with the file that
actually runs marked ``*``, its real path, the version it reports, and the
package that owns it.

Run::

    ./path_conflicts.py                # current $PATH
    ./path_conflicts.py -v             # debug logging
    ./path_conflicts.py --only-conflicts
    ./path_conflicts.py --no-versions  # do not execute foreign --version flags

Versions come from running ``COMMAND --version`` (first line of output) and
fall back to ``rpm -qf`` for the owning package. ``--no-packages`` skips RPM.
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from tabulate import tabulate

LOG = logging.getLogger("path_conflicts")

MAX_VERSION_LEN = 120
DEFAULT_WRAP_WIDTH = 100


@dataclass(frozen=True)
class PathDir:
    """One directory from ``$PATH``.

    Parameters
    ----------
    path : str
        Absolute directory path, spelled as it appears in ``$PATH``.
    real : str
        Symlink-resolved directory path, used for display and for dropping
        duplicate entries.
    kind : str
        ``"user"`` when the directory lives under the home directory,
        otherwise ``"system"``.
    order : int
        Zero-based position after resolving and deduplicating ``$PATH``,
        which is also the order in which the shell consults the directory.

    Examples
    --------
    >>> PathDir(path="/usr/bin", real="/usr/bin", kind="system", order=0).kind
    'system'
    """

    path: str
    real: str
    kind: str
    order: int = 0


@dataclass
class Occurrence:
    """A command name found in one ``$PATH`` directory.

    Parameters
    ----------
    name : str
        Executable file name, as typed in a shell.
    path_dir : PathDir
        Directory that contains it.
    file : str
        Full path to the executable inside that directory.
    real : str
        Symlink-resolved path to the executable.
    version : str
        Version string reported by the executable, if any.
    package : str
        Owning package or installation source, if any.

    Examples
    --------
    >>> occ = Occurrence("uv", PathDir("/usr/bin", "/usr/bin", "system"), "/usr/bin/uv", "/usr/bin/uv")
    >>> occ.name
    'uv'
    """

    name: str
    path_dir: PathDir
    file: str
    real: str
    version: str = ""
    package: str = field(default="")


def split_path(path_value: str) -> list[str]:
    """Split a ``$PATH``-style string into unique absolute directories.

    Empty entries are ignored, relative entries are resolved against the
    current directory, and duplicates keep their first position.

    Parameters
    ----------
    path_value : str
        Colon-separated directory list, usually ``os.environ["PATH"]``.

    Returns
    -------
    list[str]
        Directory paths in their original order, without duplicates.

    Examples
    --------
    >>> split_path("/a:/b:/a")
    ['/a', '/b']
    >>> split_path(":/a::")
    ['/a']
    """
    seen: set[str] = set()
    result: list[str] = []
    for raw in path_value.split(os.pathsep):
        if not raw:
            continue
        directory = os.path.abspath(raw)
        if directory not in seen:
            seen.add(directory)
            result.append(directory)
    return result


def path_dirs(path_value: str, home: str | None = None) -> list[PathDir]:
    """Build ``PathDir`` entries for the directories that exist in ``$PATH``.

    Directories are deduplicated by their resolved path, so ``/bin`` and
    ``/usr/bin`` collapse into one entry when ``/bin`` is a symlink.

    Parameters
    ----------
    path_value : str
        Colon-separated directory list.
    home : str, optional
        Home directory used to classify entries, defaults to ``Path.home()``.

    Returns
    -------
    list[PathDir]
        Existing directories in ``$PATH`` order.

    Examples
    --------
    >>> path_dirs("/definitely/not/here") == []
    True
    """
    home = os.path.realpath(home or Path.home())
    result: list[PathDir] = []
    seen: set[str] = set()
    for directory in split_path(path_value):
        if not os.path.isdir(directory):
            LOG.debug("skipping missing PATH entry %s", directory)
            continue
        real = os.path.realpath(directory)
        if real in seen:
            LOG.debug("skipping duplicate PATH entry %s -> %s", directory, real)
            continue
        seen.add(real)
        kind = "user" if _within(real, home) else "system"
        result.append(PathDir(path=directory, real=real, kind=kind, order=len(result)))
    return result


def iter_commands(directory: str) -> list[str]:
    """List executable file names in one directory.

    Symlinks are followed, so a link to an executable counts and a broken link
    does not. The result is sorted for stable output.

    Parameters
    ----------
    directory : str
        Directory to scan.

    Returns
    -------
    list[str]
        Executable file names.

    Examples
    --------
    >>> iter_commands("/definitely/not/here") == []
    True
    """
    try:
        entries = list(os.scandir(directory))
    except OSError as exc:
        LOG.debug("cannot scan %s: %s", directory, exc)
        return []
    names = [
        entry.name
        for entry in entries
        if entry.is_file(follow_symlinks=True) and os.access(entry.path, os.X_OK)
    ]
    return sorted(names)


def scan(dirs: list[PathDir]) -> dict[str, list[Occurrence]]:
    """Index every executable name across the given directories.

    Parameters
    ----------
    dirs : list[PathDir]
        Directories in ``$PATH`` order.

    Returns
    -------
    dict[str, list[Occurrence]]
        Command name to occurrences in ``$PATH`` order.

    Examples
    --------
    >>> scan([])
    {}
    """
    index: dict[str, list[Occurrence]] = {}
    for path_dir in dirs:
        for name in iter_commands(path_dir.path):
            file = os.path.join(path_dir.path, name)
            occurrence = Occurrence(
                name=name,
                path_dir=path_dir,
                file=file,
                real=os.path.realpath(file),
            )
            index.setdefault(name, []).append(occurrence)
    return index


def conflicting(index: dict[str, list[Occurrence]]) -> dict[str, list[Occurrence]]:
    """Return names whose occurrences point at different real files.

    Parameters
    ----------
    index : dict[str, list[Occurrence]]
        Result of :func:`scan`.

    Returns
    -------
    dict[str, list[Occurrence]]
        Only the names that resolve to more than one distinct file.

    Examples
    --------
    >>> conflicting({})
    {}
    """
    return {name: items for name, items in index.items() if _distinct_files(items) > 1}


def non_conflicting(
    index: dict[str, list[Occurrence]],
) -> dict[str, list[Occurrence]]:
    """Return names that resolve to exactly one real file.

    Parameters
    ----------
    index : dict[str, list[Occurrence]]
        Result of :func:`scan`.

    Returns
    -------
    dict[str, list[Occurrence]]
        Names that are unambiguous, even if reachable through several
        ``$PATH`` directories via symlinks.

    Examples
    --------
    >>> non_conflicting({})
    {}
    """
    return {name: items for name, items in index.items() if _distinct_files(items) == 1}


def probe_version(executable: str, timeout: float = 5.0) -> str:
    """Ask an executable for its version.

    Runs ``executable --version`` with stdin closed, from ``/``, and returns
    the first non-empty output line. Failures, timeouts, and empty output all
    produce an empty string.

    Parameters
    ----------
    executable : str
        Path to the executable to run.
    timeout : float, optional
        Seconds to wait before killing it, by default 5.0.

    Returns
    -------
    str
        First output line, truncated to ``MAX_VERSION_LEN`` characters.

    Examples
    --------
    >>> probe_version("/definitely/not/here") == ''
    True
    """
    env = dict(os.environ)
    env.setdefault("NO_COLOR", "1")
    env["TERM"] = "dumb"
    try:
        completed = subprocess.run(
            [executable, "--version"],
            check=False,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            cwd="/",
            env=env,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        LOG.debug("version probe failed for %s: %s", executable, exc)
        return ""
    output = (completed.stdout or "").strip() or (completed.stderr or "").strip()
    if not output:
        return ""
    if completed.returncode != 0 and not (completed.stdout or "").strip():
        # Usage text from a rejected --version is not a version.
        return ""
    return output.splitlines()[0].strip()[:MAX_VERSION_LEN]


def rpm_info(path: str, rpm: str = "rpm", timeout: float = 5.0) -> tuple[str, str]:
    """Look up the RPM package that owns a file.

    Parameters
    ----------
    path : str
        File to query.
    rpm : str, optional
        ``rpm`` executable to run, by default ``"rpm"``.
    timeout : float, optional
        Seconds to wait, by default 5.0.

    Returns
    -------
    tuple[str, str]
        ``(package, version)``, or ``("", "")`` when unowned or on failure.

    Examples
    --------
    >>> rpm_info("/definitely/not/here", rpm="/bin/false") == ('', '')
    True
    """
    query_format = "%{NAME} %{VERSION}-%{RELEASE}"
    try:
        completed = subprocess.run(
            [rpm, "-qf", "--queryformat", query_format, path],
            check=False,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        LOG.debug("rpm query failed for %s: %s", path, exc)
        return ("", "")
    if completed.returncode != 0:
        return ("", "")
    parts = completed.stdout.strip().split(maxsplit=1)
    if len(parts) != 2:
        return ("", "")
    return (parts[0], parts[1])


def package_label(
    path: str,
    home: str | None = None,
    rpm: str = "rpm",
    enabled: bool = True,
) -> str:
    """Describe where an executable came from.

    User-directory files are labelled by installation style (``uv``,
    ``cargo``, ``user install``); other files are looked up with ``rpm``.

    Parameters
    ----------
    path : str
        Executable path.
    home : str, optional
        Home directory, defaults to ``Path.home()``.
    rpm : str, optional
        ``rpm`` executable to run, by default ``"rpm"``.
    enabled : bool, optional
        When false, skip the RPM lookup, by default True.

    Returns
    -------
    str
        Human-readable source label, possibly empty.

    Examples
    --------
    >>> package_label("/definitely/not/here", home="/home/xk", enabled=False)
    ''
    """
    real = os.path.realpath(path)
    home_real = os.path.realpath(home or Path.home())
    if _within(real, home_real):
        if "/.local/share/uv/" in real:
            return "uv"
        if "/cargo/bin/" in real:
            return "cargo"
        if "/.local/bin/" in real:
            return "user install"
        return "user file"
    if not enabled:
        return ""
    name, version = rpm_info(path, rpm=rpm)
    return f"{name} {version}" if name else ""


def enrich(
    index: dict[str, list[Occurrence]],
    *,
    timeout: float = 5.0,
    jobs: int = 16,
    versions: bool = True,
    packages: bool = True,
    home: str | None = None,
    rpm: str = "rpm",
) -> None:
    """Fill ``version`` and ``package`` on every occurrence in ``index``.

    Probes run in parallel and are cached by ``$PATH`` file, so a command
    reachable through several directories is executed once per directory.
    The entry itself is probed instead of its symlink target, which matters for
    argv[0] dispatchers such as ccache.

    Parameters
    ----------
    index : dict[str, list[Occurrence]]
        Result of :func:`scan`, modified in place.
    timeout : float, optional
        Seconds allowed per probe, by default 5.0.
    jobs : int, optional
        Worker threads, by default 16.
    versions : bool, optional
        Run ``--version`` probes, by default True.
    packages : bool, optional
        Query RPM, by default True.
    home : str, optional
        Home directory for source classification.
    rpm : str, optional
        ``rpm`` executable to run.

    Examples
    --------
    >>> enrich({})
    """
    occurrences = [item for items in index.values() for item in items]
    files = sorted({item.file for item in occurrences})
    if not files:
        return

    def describe(file: str) -> tuple[str, str]:
        version = probe_version(file, timeout=timeout) if versions else ""
        package = package_label(file, home=home, rpm=rpm, enabled=packages)
        return (version, package)

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        described = dict(zip(files, pool.map(describe, files)))
    for item in occurrences:
        item.version, item.package = described[item.file]


def wrap_names(names: list[str], width: int = DEFAULT_WRAP_WIDTH) -> str:
    """Join command names into a wrapped comma-separated cell.

    Parameters
    ----------
    names : list[str]
        Command names.
    width : int, optional
        Target line width, by default 100.

    Returns
    -------
    str
        Comma-separated text with newlines between wrapped lines.

    Examples
    --------
    >>> wrap_names(["alpha", "beta"], width=80)
    'alpha, beta'
    """
    return "\n".join(
        textwrap.wrap(
            ", ".join(names),
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def render_conflict(
    name: str, occurrences: list[Occurrence], tablefmt: str = "simple"
) -> str:
    """Render one conflicting command as a table of its occurrences.

    Rows are sorted by ``PathDir.order`` and show resolved directory paths.
    The first row is the one the shell runs and is marked ``*``. Only
    directories that contain the command appear, so there are no empty rows.

    Parameters
    ----------
    name : str
        Command name.
    occurrences : list[Occurrence]
        Occurrences in ``$PATH`` order.
    tablefmt : str, optional
        Any :mod:`tabulate` table format, by default ``"simple"``.

    Returns
    -------
    str
        Title line followed by the table.

    Examples
    --------
    >>> render_conflict("nothing", []).splitlines()[0]
    'nothing'
    """
    rows = []
    ordered = sorted(occurrences, key=lambda item: item.path_dir.order)
    for position, item in enumerate(ordered):
        marker = "* " if position == 0 else "  "
        rows.append(
            [
                marker + item.path_dir.real,
                item.path_dir.kind,
                item.real,
                item.version or "-",
                item.package or "-",
            ]
        )
    table = tabulate(
        rows,
        headers=["PATH", "Kind", "Resolves to", "Version", "Package"],
        tablefmt=tablefmt,
        disable_numparse=True,
        missingval="-",
    )
    return f"{name}\n{table}"


def render_non_conflicting(
    dirs: list[PathDir],
    index: dict[str, list[Occurrence]],
    tablefmt: str = "simple",
    width: int = DEFAULT_WRAP_WIDTH,
) -> str:
    """Render unambiguous command names grouped by resolved ``$PATH`` directory.

    Rows follow ``PathDir.order`` and show resolved directory paths.
    Directories with no unambiguous names are omitted, so the table has no
    empty rows.

    Parameters
    ----------
    dirs : list[PathDir]
        Directories in ``$PATH`` order.
    index : dict[str, list[Occurrence]]
        Result of :func:`scan`.
    tablefmt : str, optional
        Any :mod:`tabulate` table format, by default ``"simple"``.
    width : int, optional
        Line width for the command list, by default 100.

    Returns
    -------
    str
        Table text, or ``""`` when nothing is unambiguous.

    Examples
    --------
    >>> render_non_conflicting([], {})
    ''
    """
    by_dir: dict[str, list[str]] = {}
    for name, items in index.items():
        if _distinct_files(items) == 1:
            primary = min(items, key=lambda item: item.path_dir.order)
            by_dir.setdefault(primary.path_dir.real, []).append(name)
    rows = []
    for path_dir in sorted(dirs, key=lambda item: item.order):
        names = sorted(by_dir.get(path_dir.real, []))
        if not names:
            continue
        rows.append(
            [
                path_dir.real,
                path_dir.kind,
                len(names),
                wrap_names(names, width=width),
            ]
        )
    if not rows:
        return ""
    return tabulate(
        rows,
        headers=["PATH", "Kind", "Count", "Commands"],
        tablefmt=tablefmt,
        disable_numparse=True,
    )


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser.

    Returns
    -------
    argparse.ArgumentParser
        Parser for :func:`main`.

    Examples
    --------
    >>> build_parser().parse_args([]).timeout
    5.0
    """
    parser = argparse.ArgumentParser(
        description="Report commands that collide across $PATH.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--path",
        default=os.environ.get("PATH", ""),
        help="PATH-like string to inspect",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="seconds allowed per version probe",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=16,
        help="parallel version probes",
    )
    parser.add_argument(
        "--tablefmt",
        default="simple",
        help="tabulate table format",
    )
    parser.add_argument(
        "--no-versions",
        action="store_true",
        help="do not run COMMAND --version",
    )
    parser.add_argument(
        "--no-packages",
        action="store_true",
        help="do not query rpm for the owning package",
    )
    parser.add_argument(
        "--only-conflicts",
        action="store_true",
        help="hide the non-conflicting command table",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="debug logging",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the report.

    Parameters
    ----------
    argv : list[str], optional
        Arguments, defaults to ``sys.argv[1:]``.

    Returns
    -------
    int
        Process exit status.

    Examples
    --------
    >>> main(["--path", "", "--only-conflicts"])
    1
    """
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    dirs = path_dirs(args.path)
    if not dirs:
        LOG.error("no existing directories in --path")
        return 1

    index = scan(dirs)
    conflicts = conflicting(index)
    users = sum(1 for path_dir in dirs if path_dir.kind == "user")
    LOG.debug(
        "%d directories (%d user), %d command names, %d conflicting",
        len(dirs),
        users,
        len(index),
        len(conflicts),
    )

    enrich(
        index,
        timeout=args.timeout,
        jobs=args.jobs,
        versions=not args.no_versions,
        packages=not args.no_packages,
    )

    print(
        f"PATH directories: {len(dirs)} ({users} user, "
        f"{len(dirs) - users} system); "
        f"commands: {len(index)} ({len(non_conflicting(index))} unambiguous, "
        f"{len(conflicts)} conflicting)"
    )

    if not args.only_conflicts:
        table = render_non_conflicting(dirs, index, tablefmt=args.tablefmt)
        if table:
            print("\n== Non-conflicting commands ==")
            print(table)

    if conflicts:
        print(f"\n== Conflicting commands ({len(conflicts)}) ==")
        print(
            "PATHs are shown resolved, in PATH resolution order; "
            "* is the file that runs.\n"
        )
        for name in sorted(conflicts):
            print(render_conflict(name, index[name], tablefmt=args.tablefmt))
            print()
    else:
        print("\nNo conflicting commands.")
    return 0


def _distinct_files(items: list[Occurrence]) -> int:
    """Count distinct resolved files among occurrences."""
    return len({item.real for item in items})


def _within(path: str, parent: str) -> bool:
    """Return whether ``path`` is ``parent`` or inside it."""
    try:
        return os.path.commonpath([path, parent]) == parent
    except ValueError:
        return False


if __name__ == "__main__":
    sys.exit(main())
