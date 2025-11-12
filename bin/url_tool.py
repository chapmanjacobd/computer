#!/usr/bin/python3

import argparse
import re
import sys
import unicodedata
import urllib.parse


def get_utf8_info(char):
    """
    Retrieves the Unicode name and code point for a character.
    Returns 'Not found' and None if the name is unavailable.
    """
    try:
        name = unicodedata.name(char)
        code_point = ord(char)
        return name, code_point
    except ValueError:
        return "Not found", None


def unquote_and_track(text):
    """
    Decodes percent-encoded sequences in the text and maps the resulting
    decoded characters back to their original encoded string.
    """
    # Regex to find consecutive percent-encoded bytes (e.g., %C3%A9)
    PERCENT_GROUP_RE = re.compile(r'(?:%[0-9a-fA-F]{2})+')
    # Dictionary to map the decoded character to its original percent-encoded sequence
    decoded_map = {}

    def tracker_replacer(match):
        encoded_seq = match.group(0)
        decoded_char = urllib.parse.unquote(encoded_seq)

        # We track if the decoded character is a single character AND
        # if the encoded sequence is different from the decoded character
        if len(decoded_char) == 1 and encoded_seq != decoded_char:
            decoded_map[decoded_char] = encoded_seq

        return decoded_char

    unquoted_text = PERCENT_GROUP_RE.sub(tracker_replacer, text)
    return unquoted_text, decoded_map


def process_input(text):
    """
    Decodes percent-encoded sequences and then processes the text, printing verbose
    Unicode information for non-ASCII characters or characters that were
    decoded from a percent-encoding sequence.
    """
    unquoted_text, decoded_map = unquote_and_track(text)
    prev_char_ascii = False

    for char in unquoted_text:
        is_non_ascii = ord(char) > 127
        is_decoded = char in decoded_map

        if is_non_ascii or is_decoded:
            if prev_char_ascii:
                print()

            name, code_point = get_utf8_info(char)

            # Use 'N/A' if code_point is None to prevent string formatting errors
            code_point_str = f"U+{code_point}" if code_point is not None else "N/A"

            info = f"{char} ({name}, {code_point_str}, 0x{char.encode().hex()})"

            if is_decoded:
                # Use "Unquoted" to indicate it came from a percent-encoded sequence
                info += f" [Unquoted: {decoded_map[char]}]"

            print(info)
            prev_char_ascii = False
        else:
            print(char, end='')
            prev_char_ascii = True

    if prev_char_ascii:
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Analyzes Unicode information in a percent-encoded (URL/URI) string. Reads from stdin unless an argument is provided."
    )
    # Define the input string as an optional positional argument
    parser.add_argument(
        "input_string",
        nargs='?',
        type=str,
        help="The percent-encoded string to analyze. If omitted, input is read from stdin.",
    )
    args = parser.parse_args()

    if args.input_string:
        input_text = args.input_string
    else:
        # Fallback to reading from stdin if no argument is provided
        input_text = sys.stdin.read()

    if not input_text:
        print("Error: No input provided via argument or standard input.", file=sys.stderr)
        sys.exit(1)

    process_input(input_text)


if __name__ == "__main__":
    main()
