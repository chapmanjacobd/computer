#!/usr/bin/python3

import argparse
import os
import random
import shutil
import string
import subprocess
import sys
import threading
import time

import numpy as np

try:
    import pynput  # ty: ignore[import-not-found]
except ImportError:  # pynput is only needed for the X11 fallback.
    pynput = None


def _kxkbrc(key):
    """Return one value from the KDE keyboard layout config."""
    try:
        result = subprocess.run(
            ["kreadconfig6", "--file", "kxkbrc", "--group", "Layout", "--key", key],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    return result.stdout.strip().split(",")[0].strip()


class DotoolController:
    """Type through a long-running dotool process using uinput."""

    def __init__(self, command=None):
        env = os.environ.copy()
        layout = _kxkbrc("LayoutList") or "us"
        variant = _kxkbrc("VariantList")
        env["DOTOOL_XKB_LAYOUT"] = layout
        if variant:
            env["DOTOOL_XKB_VARIANT"] = variant

        self.proc = subprocess.Popen(
            command or ["dotool"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            env=env,
        )

    def _send(self, action):
        assert self.proc.stdin is not None
        self.proc.stdin.write(action + "\n")
        self.proc.stdin.flush()

    def type(self, char):
        if char == "\n":
            self._send("key enter")
        elif char == "\t":
            self._send("key tab")
        elif char == " ":
            self._send("key space")
        elif char != "\r":
            self._send("type " + char)

    def tap(self, key):
        self._send("key " + key)

    def close(self):
        if self.proc.stdin and not self.proc.stdin.closed:
            self.proc.stdin.close()
        try:
            self.proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.proc.terminate()


class PynputController:
    """X11 fallback using pynput."""

    def __init__(self):
        if pynput is None:
            raise RuntimeError("pynput is not installed")
        self.control = pynput.keyboard.Controller()

    def type(self, char):
        self.control.type(char)

    def tap(self, key):
        assert pynput is not None
        if key == "backspace":
            self.control.tap(pynput.keyboard.Key.backspace)
        else:
            self.control.tap(key)

    def close(self):
        pass


def make_controller(backend="auto"):
    if backend == "auto":
        backend = "dotool" if shutil.which("dotool") else "pynput"
    if backend == "dotool":
        return DotoolController()
    if backend == "pynput":
        return PynputController()
    raise ValueError(f"unknown backend: {backend}")


class sim_keyboard(threading.Thread):
    def __init__(
        self,
        text,
        start_delay=1.5,
        dct_delays=None,
        delay_range=(0.07, 0.24),
        backend="auto",
        controller=None,
    ):
        threading.Thread.__init__(self)

        if dct_delays is None:
            dct_delays = {('a', 'i'): 0.12}
        self.text = text
        self.start_delay = start_delay
        self.last_char = " "
        self.dct_delays = dct_delays
        self.delay_range = delay_range
        self.control = controller or make_controller(backend)

    def run(self):
        time.sleep(self.start_delay)
        for char in self.text:
            if (self.last_char, char) not in self.dct_delays:
                self.dct_delays[(self.last_char, char)] = random.uniform(*self.delay_range)
            delay = np.random.normal(loc=float(self.dct_delays[(self.last_char, char)]), scale=0.02)

            if random.random() < np.random.normal(loc=0.1, scale=0.03):
                time.sleep(max(0.0, delay - 0.03))
                self.press_wrong_key(delay)
                time.sleep(max(0.0, delay + 0.02))
            else:
                time.sleep(max(0.0, delay - 0.03))

            self.control.type(char)
            self.last_char = char

    def press_wrong_key(self, delay):
        one_typo = 0.8
        two_typos = 0.15
        three_typos = 0.05
        num_typos = np.random.choice([1, 2, 3], p=[one_typo, two_typos, three_typos])

        for _ in range(num_typos):
            wrong_char = random.choice(string.ascii_lowercase)
            self.control.type(wrong_char)
            time.sleep(delay)

        for _ in range(num_typos):
            self.control.tap("backspace")
            time.sleep(max(0.0, np.random.normal(loc=0.05, scale=0.01)))

    def close(self):
        self.control.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Type stdin with human-like delays.")
    parser.add_argument(
        "--backend",
        choices=("auto", "dotool", "pynput"),
        default="auto",
        help="input backend (default: auto; prefers dotool)",
    )
    parser.add_argument("--verbose", action="store_true", help="print the selected backend")
    args = parser.parse_args(argv)

    text = "\n".join(sys.stdin.readlines()).replace("    ", "\t")
    backend = args.backend
    if backend == "auto":
        backend = "dotool" if shutil.which("dotool") else "pynput"
    if args.verbose:
        print(f"typer: backend={backend}", file=sys.stderr)

    keyboard_thread = sim_keyboard(text, backend=backend)
    keyboard_thread.start()
    try:
        keyboard_thread.join()
    finally:
        keyboard_thread.close()


if __name__ == "__main__":
    main()
