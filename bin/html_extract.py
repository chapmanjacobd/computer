#!/usr/bin/python3
from pathlib import Path

from bs4 import BeautifulSoup
from library import usage
from library.createdb import fs_add_metadata
from library.data.http_errors import HTTPStatus
from library.utils import arggroups, argparse_utils, devices, file_utils, iterables, printing, web
from library.utils.log_utils import log


def parse_args():
    parser = argparse_utils.ArgumentParser(usage=usage.extract_text)
    arggroups.requests(parser)
    parser.add_argument("--local-html", action="store_true", help="Treat paths as Local HTML files")
    arggroups.selenium(parser)

    # TODO: support all CSS style selectors
    parser.add_argument(
        '--classes',
        nargs='+',
        required=True,
        help='A space-separated list of CSS class names to look for (e.g., album-artist album-title).',
    )
    parser.add_argument(
        '--separator',
        type=str,
        default='\t',
        help='The string used to separate the extracted elements on the output line',
    )

    arggroups.debug(parser)
    arggroups.paths_or_stdin(parser)
    args = parser.parse_intermixed_args()
    arggroups.args_post(args, parser)

    web.requests_session(args)  # prepare requests session
    arggroups.selenium_post(args)

    return args


def extract_grouped_info(args, html_content):
    soup = BeautifulSoup(html_content, "lxml")

    all_target_elements = soup.find_all(class_=args.classes)

    grouped_by_parent = {}
    for element in all_target_elements:
        parent = element.parent
        if parent is not None:
            if parent not in grouped_by_parent:
                grouped_by_parent[parent] = []
            grouped_by_parent[parent].append(element)

    for parent, elements in grouped_by_parent.items():
        texts = [e.get_text(strip=True) for e in elements]
        yield args.separator.join(texts)


def get_text(args, url):
    is_error = False
    if not args.local_html and not url.startswith("http") and Path(url).is_file():
        text = fs_add_metadata.munge_book_tags_fast(url)
        if text:
            tags = text.get("tags")
            if tags:
                yield tags.replace(";", "\n")
        return None

    if args.selenium:
        web.selenium_get_page(args, url)

        if args.manual:
            while devices.confirm("Extract HTML from browser?"):
                markup = web.selenium_extract_html(args.driver)
                yield from extract_grouped_info(args, markup)
        else:
            for markup in web.infinite_scroll(args.driver):
                yield from extract_grouped_info(args, markup)
    else:
        if args.local_html:
            with open(url) as f:
                markup = f.read()
            url = "file://" + url
        else:
            try:
                r = web.session.get(url, timeout=120)
            except Exception:
                log.exception("Could not get a valid response from the server")
                return None
            if r.status_code == HTTPStatus.NOT_FOUND:
                log.warning("404 Not Found Error: %s", url)
                is_error = True
            else:
                r.raise_for_status()
            markup = r.content

        yield from extract_grouped_info(args, markup)

    web.sleep(args)

    if is_error:
        return None


def main() -> None:
    args = parse_args()

    if args.selenium:
        web.load_selenium(args)
    try:
        for url in file_utils.gen_paths(args):
            for s in iterables.return_unique(get_text)(args, url):
                if s is None:
                    break
                printing.pipe_print(s)
    finally:
        if args.selenium:
            web.quit_selenium(args)

if __name__ == "__main__":
    main()
