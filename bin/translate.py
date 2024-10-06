#!/usr/bin/python3
import argparse
import string
import sys

import dl_translate as dlt

mt = dlt.TranslationModel("facebook/nllb-200-distilled-600M")
LANGS = mt.available_languages()


def main():
    parser = argparse.ArgumentParser(description="Add spaces to text or read text from a file.")
    parser.add_argument('--source-lang', '-f', type=str, choices=LANGS, help='Source language')
    parser.add_argument(
        '--target-lang', '-t', type=str, choices=LANGS, default=dlt.lang.ENGLISH, help='Target language'
    )

    parser.add_argument(
        'input_paths', nargs='*', type=argparse.FileType("r"), default=[sys.stdin], help="Paths to process"
    )
    args = parser.parse_args()

    non_text = set([*string.digits, *string.whitespace, *string.punctuation])

    for path in args.input_paths:
        text = path.read()
        for line in text.splitlines():
            if any(char not in non_text for char in line):
                translated = mt.translate(line, source=args.source_lang, target=args.target_lang)
                print(translated)
            else:
                print(line)


if __name__ == "__main__":
    main()
