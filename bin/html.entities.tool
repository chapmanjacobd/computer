#!/usr/bin/python3

import html
import re
import sys
import unicodedata


def get_utf8_info(char):
    try:
        name = unicodedata.name(char)
        code_point = ord(char)
        return name, code_point
    except ValueError:
        return "Not found", None


def decode_and_track_entities(text):
    # Regex to find HTML entities: &#...; or &name;
    ENTITY_RE = re.compile(r'&(?:#\d+|#x[0-9a-fA-F]+|\w+);')
    # Use a dictionary to map the decoded character to its original entity string
    entity_map = {}

    def tracker_replacer(match):
        entity = match.group(0)
        # Unescape the entity
        decoded_char = html.unescape(entity)
        if len(decoded_char) == 1:
            # Store the decoded character and its original entity
            entity_map[decoded_char] = entity
        # Return the decoded character for the main unescaped text
        return decoded_char

    # Perform a substitution using the tracker function
    unescaped_text = ENTITY_RE.sub(tracker_replacer, text)

    return unescaped_text, entity_map


def process_input(text):
    """
    Decodes HTML entities and then processes the text, printing verbose
    Unicode information for non-ASCII characters or characters that were
    decoded from an HTML entity.
    """
    unescaped_text, entity_map = decode_and_track_entities(text)
    prev_char_ascii = False

    for char in unescaped_text:
        is_non_ascii = ord(char) > 127
        is_decoded_entity = char in entity_map

        if is_non_ascii or is_decoded_entity:
            # Add a line break if the previous block was standard ASCII text
            if prev_char_ascii:
                print()

            name, code_point = get_utf8_info(char)

            # Use 'N/A' if code_point is None to prevent string formatting errors
            code_point_str = f"U+{code_point}" if code_point is not None else "N/A"

            info = f"{char} ({name}, {code_point_str}, 0x{char.encode().hex()})"

            if is_decoded_entity:
                info += f" [Decoded: {entity_map[char]}]"

            print(info)
            prev_char_ascii = False
        else:
            # Print standard ASCII characters normally
            print(char, end='')
            prev_char_ascii = True

    # Ensure a final newline if the last item was an ASCII block
    if prev_char_ascii:
        print()


def main():
    input_text = sys.stdin.read()
    process_input(input_text)


if __name__ == "__main__":
    main()
