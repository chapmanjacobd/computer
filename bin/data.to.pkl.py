#!/usr/bin/python3
import argparse
import pickle
import pathlib

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", nargs="?", type=argparse.FileType("r"), default="-")
    parser.add_argument("output_path", nargs="?")
    args = parser.parse_args()

    if args.output_path is None:
        args.output_path = pathlib.Path(args.input_path.name).with_suffix('.pkl')

    lines = set(s.strip() for s in args.input_path.readlines())
    args.input_path.close()

    with open(args.output_path, 'wb') as f:
        pickle.dump(lines, f)
