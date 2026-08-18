#!/usr/bin/python3
import argparse
import re
import subprocess
import sys
from collections import deque
from time import sleep

REGEX_WGET2_SKIPPED = re.compile(r"URL '(.*?)' not followed \(parent ascending not allowed\)")


def get_orig(archive_url: str):
    # typically https://web.archive.org/web/TIMESTAMP/original_path
    if archive_url.count("/") > 5:
        original_url = "/".join(archive_url.split("/")[5:])

        # treat http:/ and http:// Wayback URLs as equivalent
        original_url = original_url.replace("http:///", "http://").replace("https:///", "https://")
        if not original_url.startswith(("http://", "https://")):
            original_url = original_url.replace("http:/", "http://").replace("https:/", "https://")

        return original_url
    else:
        return archive_url


def wayback_clone(initial_url):
    urls_history = {initial_url}
    url_queue = deque([initial_url])

    print(f"Starting recursive download for: {initial_url}")
    while url_queue:
        current_url = url_queue.popleft()
        print(f"\nProcessing URL: {current_url}")

        command = [
            'wget2',
            '--recursive',
            '--no-parent',
            '--level=inf',
            '--progress=none',
            '--server-response',
            '--timeout=80',
            '--dns-timeout=10',
            '--connect-timeout=8',
            '--read-timeout=45',
            '--tries=4',
            '--content-disposition',
            '--trust-server-names',
            '--no-robots',
            '--timestamping',
            '--force-directories',
            '--adjust-extension',
            '--page-requisites',
            '--convert-links',
            '--verbose',
            current_url,
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        while process.stdout:
            line = process.stdout.readline()
            if not line:
                break

            # print(line.strip(), file=sys.stderr)

            match = REGEX_WGET2_SKIPPED.search(line)
            if match:
                skipped_url = match.group(1)
                skipped_hurl = get_orig(skipped_url)

                if skipped_hurl.startswith(get_orig(initial_url)):
                    if skipped_hurl not in urls_history:
                        print(f"--> Found new child URL, adding to queue: {skipped_hurl}")
                        url_queue.append(skipped_url)
                        urls_history.add(skipped_hurl)
                else:
                    print(f"--> Skipping parent ascending URL: {skipped_hurl}")

        return_code = process.wait()
        if return_code != 0:
            print('wget2 exited with code', return_code, file=sys.stderr)

        print('Visited', len(urls_history) - len(url_queue), 'of', len(urls_history), 'queued URLs')
        sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursively download a website with wget, handling WaybackMachine --no-parent exceptions."
    )

    parser.add_argument("url", help="The starting URL for the download.")
    args = parser.parse_args()

    wayback_clone(args.url)
