#!/usr/bin/python3
import argparse
import sqlite3
import sys

def main():
    parser = argparse.ArgumentParser(description='Process some lines and store them into SQLite.')
    parser.add_argument('-n', '--height', type=int, default=1, help='Number of lines to group together')
    parser.add_argument('input_file', type=str, help='Input file path or "-" for stdin')
    parser.add_argument('output_db', type=str, help='Output SQLite database file path')
    args = parser.parse_args()

    input_source = open(args.input_file, 'r') if args.input_file != "-" else sys.stdin

    conn = sqlite3.connect(args.output_db)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS media (path TEXT)''')

    lines_buffer = []
    for line in input_source:
        line = line.strip()
        if line:
            lines_buffer.append(line)

        if len(lines_buffer) >= args.height:
            with conn:
                cur.execute('''INSERT INTO media(path) VALUES (?)''', ['\n'.join(lines_buffer)])
            lines_buffer.clear()
    if lines_buffer:
        with conn:
            cur.execute('''INSERT INTO media(path) VALUES (?)''', ['\n'.join(lines_buffer)])

    if input_source is not sys.stdin:
        input_source.close()
    conn.close()

if __name__ == '__main__':
    main()
