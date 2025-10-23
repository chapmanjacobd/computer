#!/usr/bin/env python3

import argparse


def main():
    parser = argparse.ArgumentParser(description="Convert text into NATO phonetic alphabet/spelled numbers.")
    parser.add_argument('words', metavar='WORD', type=str, nargs='+', help='The words or text to convert.')
    args = parser.parse_args()

    DICTIONARY = {
        "a": "Alfa",
        "b": "Bravo",
        "c": "Charlie",
        "d": "Delta",
        "e": "Echo",
        "f": "Foxtrot",
        "g": "Golf",
        "h": "Hotel",
        "i": "India",
        "j": "Juliett",
        "k": "Kilo",
        "l": "Lima",
        "m": "Mike",
        "n": "November",
        "o": "Oscar",
        "p": "Papa",
        "q": "Quebec",
        "r": "Romeo",
        "s": "Sierra",
        "t": "Tango",
        "u": "Uniform",
        "v": "Victor",
        "w": "Whiskey",
        "x": "X-ray",
        "y": "Yankee",
        "z": "Zulu",
        "1": "One",
        "2": "Two",
        "3": "Three",
        "4": "Four",
        "5": "Five",
        "6": "Six",
        "7": "Seven",
        "8": "Eight",
        "9": "Nine",
        "0": "Zero",
    }

    for word in args.words:
        letters = []
        for char in word.lower():
            phonetic = DICTIONARY.get(char, char)
            letters.append(phonetic)

        print(' '.join(letters))


if __name__ == "__main__":
    main()
