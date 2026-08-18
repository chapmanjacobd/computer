#!/usr/bin/python3
import argparse
import re
import sys


def parse_input_and_generate_command(input_string):
    # This regular expression is designed to capture the three key pieces of information:
    # 1. The device name (e.g., /dev/sdk1)
    # 2. The hexadecimal offset (e.g., 0x00010040)
    # 3. The space-separated list of hexadecimal bytes (e.g., 5f 42 ...)
    regex_pattern = (
        r"^(?P<device>/dev/[a-zA-Z0-9]+):\s+.*?at\soffset\s(?P<offset>0x[0-9a-fA-F]+)\s+\(.*?:\s+(?P<hex_bytes>.*)"
    )

    match = re.match(regex_pattern, input_string)

    if not match:
        print(f"Error: Could not parse the input string with the expected pattern.", file=sys.stderr)
        return None

    # Extract the named groups from the regex match
    device = match.group("device")
    offset = match.group("offset")
    hex_bytes = match.group("hex_bytes")

    # The hex_bytes string needs to be converted into a format that `printf` can use.
    # It starts as "5f 42 48...", and we need to transform it to "\x5f\x42\x48...".
    # We do this by splitting the string on spaces and prepending "\\x" to each part.
    hex_list = hex_bytes.split()
    escaped_hex_list = [f"\\x{h}" for h in hex_list]
    escaped_hex_string = "".join(escaped_hex_list)

    # Construct the final command string using f-strings for clear formatting.
    # The `printf "%d" <offset>` part is a subshell command that converts the
    # hexadecimal offset to a decimal number, which is required by `dd`.
    command = f"printf '{escaped_hex_string}' | " f"sudo dd bs=1 conv=notrunc seek=$(printf '%d' {offset}) of={device}"

    return command


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parses a log-style string and generates a dd shell command.")
    parser.add_argument(
        "input_string",
        type=str,
        help="The input string to be parsed, e.g., '/dev/sdk1: 8 bytes were erased at offset 0x00010040 (btrfs): 5f 42 48 52 66 53 5f 4d'",
    )
    args = parser.parse_args()

    command = parse_input_and_generate_command(args.input_string)
    if command:
        print(command)
