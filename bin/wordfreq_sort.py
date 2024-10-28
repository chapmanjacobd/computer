#!/usr/bin/python3
import sys

from wordfreq import zipf_frequency


def main():
    input_words = sys.stdin.read().split()

    sorted_words = sorted(input_words, key=lambda word: zipf_frequency(word, 'en'), reverse=True)

    for word in sorted_words:
        print(word)


if __name__ == "__main__":
    main()
