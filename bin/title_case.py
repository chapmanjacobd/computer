#!/usr/bin/env python

import sys

LOWERCASE_WORDS = {
    'a',
    'an',
    'the',
    'and',
    'but',
    'or',
    'for',
    'nor',
    'on',
    'at',
    'to',
    'from',
    'by',
    'in',
    'of',
    'over',
    'up',
    'with',
    'as',
    'is',
    'it',
    'of',
}


def to_custom_title_case(text):
    words = text.split()
    result_words = []

    for i, word in enumerate(words):
        if i == 0:  # always capitalize the first word
            result_words.append(word.capitalize())

        # keep specific words lowercase if they are not the first word
        elif word.lower() in LOWERCASE_WORDS:
            result_words.append(word.lower())

        else:
            result_words.append(word.capitalize())

    return ' '.join(result_words)


def main():
    try:
        for line in sys.stdin:
            processed_line = to_custom_title_case(line.rstrip())
            print(processed_line)
    except KeyboardInterrupt:
        sys.stderr.write("\n")
        sys.exit(141)
    except Exception as e:
        sys.stderr.write(f"An error occurred: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
