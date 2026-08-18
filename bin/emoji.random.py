#!/usr/bin/python3
import random
import unicodedata

def is_emoji(char):
    try:
        return unicodedata.category(char) == 'So'  # 'So' is the category for symbols, including emojis
    except TypeError:
        return False

def generate_random_emoji():
    while True:
        codepoint = random.randint(0x00A0, 0x1FAFF)
        char = chr(codepoint)

        if is_emoji(char):
            return char

        if random.random() < 0.5:  # 50% chance to try a multi-codepoint emoji
            zwj = '\u200D'  # Zero-Width Joiner
            next_codepoint = random.randint(0x00A0, 0x1FAFF)
            next_char = chr(next_codepoint)
            combined = char + zwj + next_char

            if is_emoji(combined):
                return combined

print(generate_random_emoji())
