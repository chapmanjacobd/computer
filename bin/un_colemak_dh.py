#!/usr/bin/python3
import argparse

def create_translation_maps():
    qwerty_key_to_colemak_char_map = {
        # QWERTY Top Row: q w e r t y u i o p [ ] \
        # Colemak Mod-DH Top Row: q w f p b j l u y ;
        'q': 'q', 'w': 'w', 'e': 'f', 'r': 'p', 't': 'b', 'y': 'j', 'u': 'l', 'i': 'u', 'o': 'y', 'p': ';',
        '[': '[', ']': ']', '\\': '\\', # Assuming these remain unchanged
        # QWERTY Middle Row: a s d f g h j k l ; '
        # Colemak Mod-DH Middle Row: a r s t g m n e i o
        'a': 'a', 's': 'r', 'd': 's', 'f': 't', 'g': 'g', 'h': 'm', 'j': 'n', 'k': 'e', 'l': 'i', ';': 'o',
        '\'': '\'', # Apostrophe
        # QWERTY Bottom Row: z x c v b n m , . /
        # Colemak Mod-DH Bottom Row: x c d v z k h , . /
        'z': 'x', 'x': 'c', 'c': 'd', 'v': 'v', 'b': 'z', 'n': 'k', 'm': 'h', ',': ',', '.': '.', '/': '/',

        # Uppercase letters (derived from lowercase mapping, maintaining case)
        'Q': 'Q', 'W': 'W', 'E': 'F', 'R': 'P', 'T': 'B', 'Y': 'J', 'U': 'L', 'I': 'U', 'O': 'Y', 'P': ':',
        '{': '{', '}': '}', '|': '|',
        'A': 'A', 'S': 'R', 'D': 'S', 'F': 'T', 'G': 'G', 'H': 'M', 'J': 'N', 'K': 'E', 'L': 'I', ':': 'O',
        '"': '"',
        'Z': 'X', 'X': 'C', 'C': 'D', 'V': 'V', 'B': 'Z', 'N': 'K', 'M': 'H', '<': '<', '>': '>', '?': '?',
    }

    colemak_char_to_qwerty_key_map = {}
    for qwerty_key, colemak_char in qwerty_key_to_colemak_char_map.items():
        # Handle potential duplicates if multiple QWERTY keys mapped to the same Colemak char
        # (Though in standard layouts, this is rare for primary characters)
        colemak_char_to_qwerty_key_map[colemak_char] = qwerty_key

    return qwerty_key_to_colemak_char_map, colemak_char_to_qwerty_key_map

def translate_text(text, translation_map, description):
    """
    Translates a given text using the provided mapping.
    Characters not found in the map will remain unchanged.
    """
    translated_text = []
    for char in text:
        # Use .get() with a fallback to the original character if not found
        translated_text.append(translation_map.get(char, char))
    print(f"Input ({description.split(' to ')[0]}): \"{text}\"")
    print(f"Output ({description.split(' to ')[1]}): \"{''.join(translated_text)}\"")

def main(args):
    """
    Main function to parse arguments and perform the translation based on direction.
    """
    qwerty_to_colemak_map, colemak_to_qwerty_map = create_translation_maps()

    if args.direction == 'qwerty-to-colemak':
        translate_text(args.input_text, qwerty_to_colemak_map, "QWERTY Key Presses to Colemak Mod-DH Characters")
    elif args.direction == 'colemak-to-qwerty':
        translate_text(args.input_text, colemak_to_qwerty_map, "Colemak Mod-DH Characters to QWERTY Key Presses")
    else:
        print(f"Error: Invalid direction '{args.direction}'. Choose 'qwerty-to-colemak' or 'colemak-to-qwerty'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Translate text between QWERTY key presses and Colemak Mod-DH characters."
    )
    parser.add_argument(
        "input_text",
        type=str,
        help="The text to be translated."
    )
    parser.add_argument(
        "--direction",
        type=str,
        choices=['qwerty-to-colemak', 'colemak-to-qwerty'],
        default='colemak-to-qwerty', # Default to Colemak to QWERTY as per initial example
        help="The direction of translation. 'colemak-to-qwerty' (default) or 'qwerty-to-colemak'."
    )
    args = parser.parse_args()
    main(args)

