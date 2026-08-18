#!/usr/bin/python3
import argparse
import sys

import wordfreq


def goal_function(word, freq, max_length=45):
    normalized_length = len(word) / max_length
    normalized_freq = freq / 8

    length_weight = 0.9
    freq_weight = 0.2

    return (length_weight * normalized_length) + (freq_weight * normalized_freq)


def find_best_word(text, max_length=45):
    best_word = ""
    best_score = -1.0
    for i in range(1, min(len(text), max_length) + 1):
        candidate = text[:i]
        freq = wordfreq.zipf_frequency(candidate, 'en')
        if freq > 0.0:
            score = goal_function(candidate, freq)
            if score > best_score:
                best_word = candidate
                best_score = score
    return best_word


def truncate_text(text):
    truncate_chars = ".,!?;:-()[]{}"

    truncate_index = len(text)  # default to the end of the string if no match is found
    for char in truncate_chars:
        index = text.find(char)
        if index != -1:
            truncate_index = min(truncate_index, index)

    truncated_text = text[:truncate_index]
    return truncated_text


def add_spaces_to_text(text):
    words = []
    while text:
        word_text = truncate_text(text)
        if len(word_text) == 0:
            words[-1] += text[:1]
            text = text[1:]
            continue

        best_word = find_best_word(word_text)
        words.append(best_word)
        text = text[len(best_word) :]

    spaced_text = ' '.join(words)
    print(spaced_text)


def main():
    parser = argparse.ArgumentParser(description="Add spaces to text or read text from a file.")
    parser.add_argument(
        'input_paths', nargs='*', type=argparse.FileType("r"), default=[sys.stdin], help="Paths to process"
    )
    args = parser.parse_args()

    for path in args.input_paths:
        text = path.read()
        add_spaces_to_text(text)


if __name__ == "__main__":
    main()
