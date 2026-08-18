#!/usr/bin/python3
import argparse

from bs4 import BeautifulSoup
from library.utils import web


from library.utils import arggroups, argparse_utils, shell_utils, web


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.requests(parser)
    parser.add_argument("--local-html", action="store_true", help="Treat paths as Local HTML files")
    arggroups.selenium(parser)
    arggroups.debug(parser)
    parser.add_argument("--artist-only", action="store_true", help="Only print the artist name.")

    arggroups.paths_or_stdin(parser)
    args = parser.parse_intermixed_args()
    arggroups.args_post(args, parser)

    web.requests_session(args)  # prepare requests session
    arggroups.selenium_post(args)

    return args


def get_spotify_playlist_tracks(args, url):
    if getattr(args, "local_html", False):
        with open(url) as f:
            response = f.read()
    else:
        response = web.get(args, url)
        if response:
            response = response.text

    if not response:
        print("Could not get a response")
        return

    soup = BeautifulSoup(response, 'html.parser')
    tracklist_rows = soup.find_all('div', {'data-testid': 'tracklist-row'})

    if not tracklist_rows:
        print("Could not find any tracks. The HTML structure may have changed.")
        raise
        return

    for row in tracklist_rows:
        try:
            # New selector for track title
            track_title = row.find('a', {'data-testid': 'internal-track-link'}).text.strip()

            # New selector for artist name
            artist_link = row.find('a', href=lambda href: href and href.startswith('/artist/'))
            artist_name = artist_link.text.strip() if artist_link else "N/A"

            if args.artist_only:
                print(artist_name)
            else:
                # New selector for album title
                album_link = row.find('a', href=lambda href: href and href.startswith('/album/'))
                album_title = album_link.text.strip() if album_link else "N/A"
                print(f"{track_title}\t{album_title}\t{artist_name}")

        except (AttributeError, IndexError):
            continue


def main():
    parser = argparse.ArgumentParser(description="Scrape a Spotify playlist for track details.")
    parser.add_argument("urls", nargs="+", help="The URL of the Spotify playlist.")

    args = parse_args()

    if args.selenium:
        web.load_selenium(args)
    try:
        for url in shell_utils.gen_paths(args):
            get_spotify_playlist_tracks(args, url)
    finally:
        if args.selenium:
            web.quit_selenium(args)


if __name__ == "__main__":
    main()
