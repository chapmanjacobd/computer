#!/usr/bin/python

import sys


def get_total_lines(file_path):
    try:
        with open(file_path) as f:
            return sum(1 for line in f)
    except FileNotFoundError:
        try:
            return int(file_path)
        except ValueError:
            print("Error: The specified argument is neither an integer nor a valid file path.")
            sys.exit(1)


def convert_to_percentage(total_lines, line_number):
    percentage = (line_number / total_lines) * 100
    return f"{percentage:.2f}%"


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <file path or total number of lines>")
        sys.exit(1)

    total_lines = get_total_lines(sys.argv[1])

    for line in sys.stdin:
        try:
            line_number = int(line.split(':')[0])
            percentage = convert_to_percentage(total_lines, line_number)
            print(percentage, end=' ')
            print(line.split(':', 1)[1], end='')
        except ValueError:
            print(line, end='')


if __name__ == "__main__":
    main()
