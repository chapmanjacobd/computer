#!/usr/bin/python3
import argparse
import time
import webbrowser

from library.utils import shell_utils, arggroups


def main():
    parser = argparse.ArgumentParser(description="Open links from stdin in the web browser.")
    parser.add_argument('-n', type=int, default=10, help="Number of links to open before sleeping (default: 10)")

    arggroups.paths_or_stdin(parser)
    args = parser.parse_args()

    links = list(shell_utils.gen_paths(args))

    for i, link in enumerate(links):
        webbrowser.open(link, new=2, autoraise=False)
        print(link)

        if i + 1 >= args.n:
            time.sleep(1.5)


if __name__ == "__main__":
    main()
