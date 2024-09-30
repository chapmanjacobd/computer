#!/usr/bin/python3
import argparse
import sys
import webbrowser
import time

def main():
    parser = argparse.ArgumentParser(description="Open links from stdin in the web browser.")
    parser.add_argument('-n', type=int, default=10, help="Number of links to open before sleeping (default: 10)")
    args = parser.parse_args()

    links = sys.stdin.read().splitlines()

    for i, link in enumerate(links):
        webbrowser.open(link, new=2, autoraise=False)
        print(link)

        if (i + 1) % args.n == 0:
            time.sleep(1.5)

if __name__ == "__main__":
    main()
