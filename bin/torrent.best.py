#!/usr/bin/python3
"""Pick the best torrent from a /movie/ or /tv/ table and download it.

The ranking is a Python port of the in-browser sorting script: seeders,
completed count, audio/subtitle tracks, freeleech, age, size, and resolution.
A selected /torrent/ page downloads its .torrent plus the newest downloadable
English subtitle into --prefix (default: ~/Downloads).
"""

import math
import re
import sys
from dataclasses import dataclass
from functools import cmp_to_key
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

from bs4 import BeautifulSoup

from library.utils import arggroups, argparse_utils, path_utils, shell_utils, web
from library.utils.log_utils import log

WEIGHTS = {
    "seeders": 0.2,  # log(seeders + 1); fewer seeders is preferred
    "completed": 0.1,
    "audio": 0.6,
    "subtitles": 0.1,
    "free": 0.3,
    "age": 3.8,
    "size": 1.2,  # log(sizeMB + 1); larger is penalized
    "resolution": 8.5,
}

AGE_HALF_LIFE = 5.0

DEFAULT_COLUMNS = {"age": 3, "size": 4, "seeders": 5, "leechers": 6, "completed": 7}

AGE_UNITS = [
    (r"(\d+(?:\.\d+)?)\s*years?", 365),
    (r"(\d+(?:\.\d+)?)\s*months?", 30),
    (r"(\d+(?:\.\d+)?)\s*weeks?", 7),
    (r"(\d+(?:\.\d+)?)\s*days?", 1),
    (r"(\d+(?:\.\d+)?)\s*hours?", 1 / 24),
    (r"(\d+(?:\.\d+)?)\s*minutes?", 1 / 1440),
]

SIZE_UNITS = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}


@dataclass
class TorrentCandidate:
    url: str
    title: str
    row: object
    columns: dict
    score: float
    seeders: int
    has_english_subtitles: bool


@dataclass
class TorrentPage:
    title: str
    download_url: str | None
    subtitle_url: str | None
    subtitle_age_years: float | None
    is_english_subtitle: bool


def parse_args():
    parser = argparse_utils.ArgumentParser(description=__doc__)

    arggroups.requests(parser)
    arggroups.download(parser, profile=False, safe=False)
    arggroups.selenium(parser)
    parser.add_argument(
        "--no-selenium",
        dest="selenium",
        action="store_false",
        help="Use plain HTTP requests instead of Selenium",
    )
    parser.set_defaults(selenium=True, cookies_from_browser="firefox", prefix="~/Downloads")

    parser.add_argument(
        "--local-html",
        action="store_true",
        help="Treat paths as local HTML files instead of URLs",
    )
    parser.add_argument(
        "--torrent-html",
        help="Local /torrent/ HTML to use after selecting from --local-html",
    )
    parser.add_argument(
        "--select-only",
        action="store_true",
        help="Only print the selected /torrent/ page URL; do not download",
    )
    parser.add_argument(
        "--wait",
        type=float,
        default=10,
        metavar="SECONDS",
        help="When using Selenium, wait up to N seconds for torrent rows to appear",
    )
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser)
    args = parser.parse_intermixed_args()

    if args.local_html:
        args.selenium = False
    arggroups.args_post(args, parser)

    web.requests_session(args)  # prepare requests session / cookie jar
    if args.selenium:
        arggroups.selenium_post(args)

    return args


# ============================================================================
# Table parsing
# ============================================================================


def build_column_map(table):
    columns = dict(DEFAULT_COLUMNS)
    for index, th in enumerate(table.select("thead th")):
        title = (th.get("data-original-title") or th.get("title") or th.get_text() or "").strip().lower()
        if "size" in title:
            columns["size"] = index
        elif "seed" in title or title == "s":
            columns["seeders"] = index
        elif "leech" in title or title == "l":
            columns["leechers"] = index
        elif "completed" in title or title == "c":
            columns["completed"] = index
        elif "age" in title or "uploaded" in title:
            columns["age"] = index
        elif "comment" in title:
            columns["comments"] = index
        elif "torrents-filename" in (th.get("class") or []):
            columns["filename"] = index
        elif title in {"file", "name", "title"}:
            columns["filename"] = index
        elif th.select_one('a[href*="download"], .torrent-download-icon, i.fa-download'):
            columns["download"] = index
    return columns


def get_cell(row, column):
    if column is None:
        return None
    cells = row.find_all("td")
    return cells[column] if 0 <= column < len(cells) else None


def parse_size(size_string):
    match = re.fullmatch(r"([\d.]+)\s*([KMGT]?B)", size_string.strip(), re.IGNORECASE)
    if not match:
        return 0
    return float(match.group(1)) * SIZE_UNITS.get(match.group(2).upper(), 1)


def get_size_mb(row, columns):
    cell = get_cell(row, columns.get("size"))
    if cell is None:
        return 0
    return parse_size(cell.get_text().strip()) / (1024**2)


def first_int(text):
    match = re.search(r"\d[\d,]*", text or "")
    return int(match.group().replace(",", "")) if match else 0


def get_seeders(row, columns):
    cell = get_cell(row, columns.get("seeders"))
    return first_int(cell.get_text()) if cell is not None else 0


def get_completed(row, columns):
    cell = get_cell(row, columns.get("completed"))
    return first_int(cell.get_text()) if cell is not None else 0


def age_years_from_text(text):
    """Parse relative ages (eg. '4 months', '3 days 18 hours')."""
    text = (text or "").lower()
    total_days = 0.0
    matched = False
    for pattern, days_per_unit in AGE_UNITS:
        for match in re.finditer(pattern, text):
            total_days += float(match.group(1)) * days_per_unit
            matched = True
    return total_days / 365 if matched else None


def get_age_years(row, columns):
    cell = get_cell(row, columns.get("age"))
    if cell is None:
        return 0
    return age_years_from_text(cell.get_text()) or 0


def get_section_by_text(row, keyword):
    for element in row.select(".badge-extra"):
        strong = element.find("strong")
        if strong and strong.get_text(strip=True) == f"{keyword}:":
            return element
    return None


def get_subtitle_count(row):
    section = get_section_by_text(row, "Sub")
    return len(section.select(".flag-icon")) if section is not None else 0


def get_audio_count(row):
    section = get_section_by_text(row, "Audio")
    return len(section.select(".flag-icon")) if section is not None else 0


def has_english_subtitles(row):
    return row.select_one(".flag-icon-gb") is not None or row.select_one('[title="English"]') is not None


def has_free_download(row):
    return row.select_one(".fa-star.text-gold") is not None


def get_resolution_rank(row):
    text = row.get_text(" ", strip=True).lower()
    if re.search(r"\b720p\b", text):
        return 0.1
    if re.search(r"\b576p\b", text):
        return 0.2
    if re.search(r"\b540p\b", text):
        return 0.8
    if re.search(r"\b1080p\b", text):
        return 1.2
    if re.search(r"\bbdrip\b", text):
        return 1.1
    if re.search(r"\b480p\b", text):
        return 3
    if re.search(r"\b720i\b", text):
        return 4
    if re.search(r"\b576i\b", text):
        return 4.2
    if re.search(r"\b540i\b", text):
        return 4.8
    if re.search(r"\b1080i\b", text):
        return 5.2
    if re.search(r"\b480i\b", text):
        return 6
    if re.search(r"\bdvdrip\b", text) or re.search(r"\bdvd\b", text):
        return 10
    if re.search(r"\b2160p\b", text) or re.search(r"\b4k\b", text):
        return 9
    return 7


def get_qualitative_score(row, columns):
    seeders = get_seeders(row, columns)
    completed = get_completed(row, columns)
    audio_count = get_audio_count(row)
    subtitle_count = get_subtitle_count(row)
    size_mb = get_size_mb(row, columns)
    age_years = get_age_years(row, columns)
    free = 1 if has_free_download(row) else 0
    resolution_rank = get_resolution_rank(row)

    return (
        WEIGHTS["completed"] * math.log2(completed + 1)
        + WEIGHTS["audio"] * math.log2(audio_count + 1)
        + WEIGHTS["subtitles"] * math.log2(subtitle_count + 1)
        + WEIGHTS["free"] * free
        + WEIGHTS["age"] * math.exp(-age_years / AGE_HALF_LIFE)
        + WEIGHTS["resolution"] * (1 / (resolution_rank + 1))
        - WEIGHTS["seeders"] * math.log2(seeders + 1)
        - WEIGHTS["size"] * math.log2(size_mb + 1)
    )


def compare_rows(a, b, columns):
    a_seed, b_seed = get_seeders(a, columns) > 0, get_seeders(b, columns) > 0
    if a_seed != b_seed:
        return -1 if a_seed else 1

    a_sub, b_sub = has_english_subtitles(a), has_english_subtitles(b)
    if a_sub != b_sub:
        return -1 if a_sub else 1

    a_score = get_qualitative_score(a, columns)
    b_score = get_qualitative_score(b, columns)
    if a_score == b_score:
        return 0
    return -1 if a_score > b_score else 1


def sort_torrent_rows(rows, columns):
    return sorted(rows, key=cmp_to_key(lambda a, b: compare_rows(a, b, columns)))


def find_torrent_tables(soup):
    tables = []
    for table in soup.find_all("table"):
        has_torrent_rows = any(
            row.select_one(".torrent-file") or row.select_one("a.torrent-filename") for row in table.find_all("tr")
        )
        if has_torrent_rows:
            tables.append(table)
            continue

        headers = [th.get_text(" ", strip=True).lower() for th in table.select("thead th")]
        has_size = any("size" in header for header in headers)
        has_peers = any(
            header in {"s", "l"} or "seed" in header or "leech" in header for header in headers
        )
        has_detail_link = any(
            re.search(r"/torrent/\d", urlparse(anchor["href"]).path) for anchor in table.find_all("a", href=True)
        )
        if has_size and has_peers and has_detail_link:
            tables.append(table)
    return tables


def table_rows(table):
    body = table.find("tbody") or table
    return [row for row in body.find_all("tr") if row.find("td", recursive=False)]


def absolute_url(href, base_url=None):
    if not href:
        return None
    if base_url and base_url.startswith(("http://", "https://")):
        return urljoin(base_url, href)
    return href


def detail_url_from_row(row, base_url=None, columns=None):
    # The filename anchor is the canonical detail link, even if the site
    # changes its URL shape (eg. /t/123 instead of /torrent/123).
    anchor = row.select_one("a.torrent-filename[href]")
    if anchor is not None:
        return absolute_url(anchor["href"], base_url)

    filename_cell = get_cell(row, (columns or {}).get("filename"))
    if filename_cell is not None:
        anchor = filename_cell.find("a", href=True)
        if anchor is not None:
            return absolute_url(anchor["href"], base_url)

    for anchor in row.find_all("a", href=True):
        path = urlparse(anchor["href"]).path
        if re.search(r"/torrent/\d", path):
            return absolute_url(anchor["href"], base_url)
    return None


def row_title(row, columns=None):
    anchor = row.select_one("a.torrent-filename")
    if anchor is not None:
        return anchor.get_text(" ", strip=True)
    filename_cell = get_cell(row, (columns or {}).get("filename"))
    if filename_cell is not None:
        return filename_cell.get_text(" ", strip=True)
    return row.get_text(" ", strip=True)


def best_torrent_from_soup(soup, base_url=None):
    """Return the highest-ranked torrent row across every torrent table."""
    candidates = []
    tables = find_torrent_tables(soup)
    log.debug("Found %d torrent table(s)", len(tables))

    for table in tables:
        columns = build_column_map(table)
        for row in table_rows(table):
            url = detail_url_from_row(row, base_url, columns)
            if not url:
                continue
            candidates.append(
                TorrentCandidate(
                    url=url,
                    title=row_title(row, columns),
                    row=row,
                    columns=columns,
                    score=get_qualitative_score(row, columns),
                    seeders=get_seeders(row, columns),
                    has_english_subtitles=has_english_subtitles(row),
                )
            )

    if not candidates:
        log.debug("Found %d torrent row(s) without a usable detail URL", len(soup.select(".torrent-file")))
        return None

    return max(candidates, key=lambda c: (c.seeders > 0, c.has_english_subtitles, c.score))


# ============================================================================
# /torrent/ page parsing
# ============================================================================


def row_label(row):
    cells = row.find_all("td", recursive=False)
    if len(cells) < 2:
        return None
    strong = cells[0].find("strong")
    if strong is None:
        return None
    label = strong.get_text(" ", strip=True)
    return label.casefold() if label else None


def find_details_table(soup):
    for table in soup.find_all("table"):
        labels = {label for row in table.find_all("tr") if (label := row_label(row))}
        if "title" in labels and ("download" in labels or "info hash" in labels):
            return table
    return None


def is_torrent_detail_page(soup):
    return find_details_table(soup) is not None


def is_torrent_url(url):
    return url.startswith(("http://", "https://")) and bool(re.search(r"/torrent/\d", urlparse(url).path))


def is_listing_url(url):
    return bool(re.search(r"/(?:movie|movies|tv|series)/", urlparse(url).path, re.IGNORECASE))


def details_value(table, label):
    if table is None:
        return None
    for row in table.find_all("tr"):
        if row_label(row) == label.casefold():
            cells = row.find_all("td", recursive=False)
            return cells[1] if len(cells) >= 2 else None
    return None


def download_link(cell, path_fragment):
    if cell is None:
        return None
    for anchor in cell.find_all("a", href=True):
        if path_fragment in anchor["href"]:
            return anchor["href"]
    return None


def subtitle_candidates(cell):
    candidates = []
    if cell is None:
        return candidates

    for table in cell.find_all("table"):
        headers = [th.get_text(" ", strip=True).casefold() for th in table.select("thead th")]
        column = {name: index for index, name in enumerate(headers)}
        language_index = column.get("language", 0)
        download_index = column.get("download", 1)
        upload_index = column.get("uploaded")

        body = table.find("tbody") or table
        for row in body.find_all("tr"):
            cells = row.find_all("td", recursive=False)
            if len(cells) <= max(language_index, download_index):
                continue

            language_cell = cells[language_index]
            language_text = language_cell.get_text(" ", strip=True).casefold()
            english = (
                language_cell.select_one(".flag-icon-gb") is not None
                or language_cell.select_one('[title="English"]') is not None
                or "english" in language_text
            )
            if not english:
                continue

            href = download_link(cells[download_index], "/download/subtitle/")
            if not href:
                continue

            upload_cell = None
            if upload_index is not None and upload_index < len(cells):
                upload_cell = cells[upload_index]
            else:
                for candidate_cell in cells:
                    if age_years_from_text(candidate_cell.get_text()) is not None:
                        upload_cell = candidate_cell
                        break

            age = age_years_from_text(upload_cell.get_text()) if upload_cell is not None else None
            downloads_index = column.get("downloads")
            downloads = first_int(cells[downloads_index].get_text()) if downloads_index is not None and downloads_index < len(cells) else 0
            candidates.append((age, downloads, href))

    return candidates


def parse_torrent_page(soup, base_url=None):
    table = find_details_table(soup)
    title_cell = details_value(table, "Title")
    title = title_cell.get_text(" ", strip=True) if title_cell is not None else ""
    if not title:
        heading = soup.select_one("h1")
        title = heading.get_text(" ", strip=True) if heading is not None else ""

    download_cell = details_value(table, "Download")
    torrent_url = download_link(download_cell, "/download/torrent/")
    if torrent_url is None:
        # Be tolerant of sites that put the .torrent link outside the Download row
        anchor = soup.select_one('a[href*="/download/torrent/"]')
        torrent_url = anchor["href"] if anchor is not None else None

    candidates = subtitle_candidates(details_value(table, "Subtitles"))
    newest = min(candidates, key=lambda c: (c[0] is None, c[0] if c[0] is not None else 0, -c[1])) if candidates else None

    return TorrentPage(
        title=title,
        download_url=absolute_url(torrent_url, base_url),
        subtitle_url=absolute_url(newest[2], base_url) if newest else None,
        subtitle_age_years=newest[0] if newest else None,
        is_english_subtitle=newest is not None,
    )


# ============================================================================
# Fetching and downloading
# ============================================================================


def wait_for_selenium_content(args):
    timeout = getattr(args, "wait", 10)
    if timeout <= 0:
        return
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait

        WebDriverWait(args.driver, timeout).until(
            lambda driver: driver.find_elements(
                By.CSS_SELECTOR, '.torrent-file, a.torrent-filename, a[href*="/download/torrent/"]'
            )
        )
    except Exception as excinfo:
        log.debug("Torrent content did not appear within %s seconds: %s", timeout, excinfo)


def fetch_html(args, url):
    if getattr(args, "local_html", False):
        path = Path(url).expanduser()
        if not path.is_file() and getattr(args, "torrent_html", None) and url.startswith(("http://", "https://")):
            path = Path(args.torrent_html).expanduser()
        if not path.is_file():
            message = f"Local HTML file not found: {path}"
            if url.startswith(("http://", "https://")):
                message += " (use --torrent-html for the selected /torrent/ page)"
            raise FileNotFoundError(message)
        return path.read_text(encoding="utf-8", errors="replace")

    if getattr(args, "selenium", False):
        web.selenium_get_page(args, url)
        wait_for_selenium_content(args)
        html = args.driver.page_source
    else:
        response = web.get(args, url)
        html = response.text if response is not None else None

    log.debug("Fetched %s bytes from %s", len(html) if html else 0, url)
    return html


def filename_from_url(url):
    filename = Path(unquote(urlparse(url).path)).name or "download"
    return path_utils.clean_path(filename.encode(), max_name_len=255)


def download_file(args, url):
    destination = Path(args.prefix).expanduser()
    destination.mkdir(parents=True, exist_ok=True)
    output_path = destination / filename_from_url(url)
    return web.download_url(args, url, str(output_path))


def process_url(args, url):
    html = fetch_html(args, url)
    if not html:
        log.warning("Could not get a response for %s", url)
        return

    soup = BeautifulSoup(html, "html.parser")
    base_url = None if getattr(args, "local_html", False) else url

    if is_torrent_url(url) or (is_torrent_detail_page(soup) and not is_listing_url(url)):
        torrent_url = url
        details = parse_torrent_page(soup, base_url)
    else:
        candidate = best_torrent_from_soup(soup, base_url)
        if candidate is None:
            if find_torrent_tables(soup):
                log.warning("Found torrent table(s) in %s, but no rows had a usable detail link", url)
            else:
                log.warning(
                    "Could not find any torrent rows in %s (try a larger --wait if the page loads them dynamically)",
                    url,
                )
            return

        torrent_url = candidate.url
        if getattr(args, "select_only", False):
            print(torrent_url)
            return

        log.info("Selected %s (%s seeders, score %.3f)", candidate.title, candidate.seeders, candidate.score)
        torrent_html = fetch_html(args, torrent_url)
        if not torrent_html:
            log.warning("Could not get a response for %s", torrent_url)
            return
        details = parse_torrent_page(BeautifulSoup(torrent_html, "html.parser"), torrent_url)

    if getattr(args, "select_only", False):
        print(torrent_url)
        return

    if not details.download_url:
        log.warning("Could not find a download link on %s", torrent_url)
        return

    downloaded = download_file(args, details.download_url)
    if downloaded:
        print(downloaded)

    if details.subtitle_url:
        downloaded = download_file(args, details.subtitle_url)
        if downloaded:
            print(downloaded)
    else:
        log.info("No downloadable English subtitle found on %s", torrent_url)


def main():
    args = parse_args()

    try:
        for url in shell_utils.gen_paths(args):
            process_url(args, url)
    finally:
        if getattr(args, "selenium", False) and getattr(args, "driver", None):
            web.quit_selenium(args)


if __name__ == "__main__":
    sys.exit(main())
