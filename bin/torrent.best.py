#!/usr/bin/python3
"""Pick the best torrent from a listing table and download it.

The ranking is a Python port of the in-browser sorting script: seeders,
completed count, audio/subtitle tracks, freeleech, age, size, and resolution.
Full disc images are ranked as DVDs, so WEB-DL releases are preferred over them.
Listing tables (including Gazelle-style /torrents.php?id= pages, their
activity_info cards, and grouped similar-torrents tables) are detected from
their contents rather than by URL. Torrents carrying a taglist=horror link are
printed to stderr and skipped.
Rows with a direct download link are downloaded without fetching the detail page;
other selected /torrent/ pages download their .torrent plus the newest
downloadable English subtitle into --prefix (default: ~/Downloads).

Links are paced with --sleep-links (default: 3 seconds). If a 429 or 403 is
received, downloads stop immediately; remaining movie/tv pages are still
evaluated and the selected /torrent/ links are appended to
~/.local/data/torrent.best/$domain.list.

With --drain-backlog, every .list file in ~/.local/data/torrent.best/ is processed
instead: each line is downloaded and removed from its file once handled. On a
429 or 403 the run stops and the file keeps the links that were not processed.
"""

import math
import re
import sys
import time
from dataclasses import dataclass, field
from functools import cmp_to_key
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse

from bs4 import BeautifulSoup

from library.data.http_errors import HTTPTooManyRequestsError, UnrecoverableError
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
DEFAULT_SLEEP_LINKS = 3.0
TORRENT_LIST_ROOT = Path("~/.local/data/torrent.best")
BLOCKED_STATUSES = {403, 429}

DEFAULT_COLUMNS = {"age": 3, "size": 4, "seeders": 5, "leechers": 6, "completed": 7}

# Grouped listings put the type in a row header and use actions with a colspan,
# so their cells are found by class instead of by header index.
GROUPED_COLUMNS = {
    "filename": ".torrent-search--grouped__overview",
    "download": ".torrent-search--grouped__download",
    "size": ".torrent-search--grouped__size",
    "seeders": ".torrent-search--grouped__seeders",
    "leechers": ".torrent-search--grouped__leechers",
    "completed": ".torrent-search--grouped__completed",
    "age": ".torrent-search--grouped__age",
}

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
    download_url: str | None = None
    is_horror: bool = False


@dataclass
class TorrentPage:
    title: str
    download_url: str | None
    subtitle_url: str | None
    subtitle_age_years: float | None
    is_english_subtitle: bool


@dataclass
class RunState:
    downloads_blocked: bool = False
    network_stopped: bool = False
    remaining_torrent_urls: list[str] = field(default_factory=list)
    torrents_downloaded: int = 0


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
        "--drain-backlog",
        "--backlog",
        dest="drain_backlog",
        action="store_true",
        help="Process every .list file in ~/.local/data/torrent.best/ and remove links once downloaded",
    )
    parser.add_argument(
        "--wait",
        type=float,
        default=10,
        metavar="SECONDS",
        help="When using Selenium, wait up to N seconds for torrent rows to appear",
    )
    parser.add_argument(
        "--sleep-links",
        type=float,
        default=DEFAULT_SLEEP_LINKS,
        metavar="SECONDS",
        help="Sleep N seconds between each page fetch or download link (default: 3)",
    )
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser, required=False)
    args = parser.parse_intermixed_args()

    if getattr(args, "drain_backlog", False):
        if args.paths:
            log.warning("Ignoring positional paths because --drain-backlog reads the .list files")
    elif args.paths is None:
        args.paths = argparse_utils.read_stdin(parser.prog)

    if args.local_html:
        args.selenium = False
    arggroups.args_post(args, parser)

    web.requests_session(args)  # prepare requests session / cookie jar
    disable_429_retry(web.session)
    if args.selenium:
        arggroups.selenium_post(args)

    return args


def disable_429_retry(session):
    """Let 429 responses reach the caller immediately instead of backing off."""
    for prefix in ("http://", "https://"):
        adapter = session.get_adapter(prefix)
        retry = getattr(adapter, "max_retries", None)
        if retry is not None and 429 in getattr(retry, "status_forcelist", ()):
            adapter.max_retries = retry.new(
                status_forcelist=[status for status in retry.status_forcelist if status != 429]
            )


# ============================================================================
# Table parsing
# ============================================================================


def header_cells(table):
    """Return the cells of the first header row, whichever markup the site uses."""
    thead = table.find("thead")
    if thead is not None:
        header_row = thead.find("tr")
        if header_row is not None:
            return header_row.find_all(["td", "th"], recursive=False)

    for row in table.find_all("tr"):
        classes = [str(value).casefold() for value in row.get("class", [])]
        if any("colhead" in value for value in classes) or row.select_one(".colhead, .colhead_dark"):
            return row.find_all(["td", "th"], recursive=False)

    for row in table.find_all("tr"):
        if row.find("th", recursive=False):
            return row.find_all(["td", "th"], recursive=False)

    # Bare tables are common; treat the first link-free row of known labels as the header.
    first_row = table.find("tr")
    if first_row is not None and first_row.find("a", href=True) is None:
        cells = first_row.find_all(["td", "th"], recursive=False)
        labels = [cell.get_text(" ", strip=True).casefold() for cell in cells]
        known = ("size", "seed", "leech", "snatch", "completed", "torrent")
        if sum(any(word in label for word in known) for label in labels) >= 2:
            return cells

    return []


def header_label(cell):
    """Return a header cell's label, preferring tooltips over icon-only text."""
    return (cell.get("data-original-title") or cell.get("title") or cell.get_text() or "").strip().lower()


def is_grouped_table(table):
    return table.select_one('[class*="torrent-search--grouped__"]') is not None


def build_column_map(table):
    if is_grouped_table(table):
        return dict(GROUPED_COLUMNS)

    columns = dict(DEFAULT_COLUMNS)
    for index, cell in enumerate(header_cells(table)):
        title = header_label(cell)
        if "size" in title:
            columns["size"] = index
        elif "seed" in title or title == "s":
            columns["seeders"] = index
        elif "leech" in title or title == "l":
            columns["leechers"] = index
        elif "snatch" in title or "completed" in title or title in {"c", "dl"} or "downloads" in title:
            columns["completed"] = index
        elif "age" in title or "uploaded" in title or "date" in title or "created" in title:
            columns["age"] = index
        elif "comment" in title:
            columns["comments"] = index
        elif "torrents-filename" in (cell.get("class") or []) or title in {
            "file",
            "name",
            "title",
            "torrent",
            "torrents",
            "release",
        }:
            columns["filename"] = index
        elif cell.select_one('a[href*="download"], .torrent-download-icon, i.fa-download'):
            columns["download"] = index
    return columns


def get_cell(row, column):
    if column is None:
        return None
    if isinstance(column, str):
        return row.select_one(column)
    cells = row.find_all("td")
    return cells[column] if 0 <= column < len(cells) else None


def parse_size(size_string):
    match = re.fullmatch(r"([\d.]+)\s*([KMGT]?)i?B", size_string.strip(), re.IGNORECASE)
    if not match:
        return 0
    return float(match.group(1)) * SIZE_UNITS.get(match.group(2).upper() + "B", 1)


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
    return (
        row.select_one(
            ".fa-star.text-gold,"
            " [data-bs-original-title='Free Download'],"
            " [data-original-title='Free Download'],"
            " [aria-label='Free Download'],"
            " [title='Free Download']"
        )
        is not None
    )


def grouped_type_text(row):
    """Return the type header shared by a grouped listing row (eg. 'Full Disc')."""
    current = row
    while current is not None:
        header = current.find("th", recursive=False)
        if header is not None and any("similar-torrents__type" in value for value in element_classes(header)):
            return header.get_text(" ", strip=True)
        current = current.find_previous_sibling("tr")
    return ""


def get_resolution_rank(row):
    text = f"{grouped_type_text(row)} {row.get_text(' ', strip=True)}".lower()
    if "full disc" in text or "full-disc" in text:
        return 10  # a full disc image is sized like a DVD
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


def qualitative_score(
    *,
    seeders,
    completed,
    size_mb,
    age_years=0,
    audio_count=0,
    subtitle_count=0,
    free=0,
    resolution_rank=7,
):
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


def get_qualitative_score(row, columns):
    return qualitative_score(
        seeders=get_seeders(row, columns),
        completed=get_completed(row, columns),
        audio_count=get_audio_count(row),
        subtitle_count=get_subtitle_count(row),
        size_mb=get_size_mb(row, columns),
        age_years=get_age_years(row, columns),
        free=1 if has_free_download(row) else 0,
        resolution_rank=get_resolution_rank(row),
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


def url_query(href):
    return parse_qs(urlparse(href or "").query)


def is_action_download(href):
    return url_query(href).get("action", [""])[0].casefold() == "download"


def is_download_href(href):
    path = urlparse(href or "").path
    return path.endswith("/download") or "/download/" in path or is_action_download(href)


def is_torrent_detail_link(href):
    if is_download_href(href):
        return False

    path = urlparse(href or "").path
    if re.search(r"/(?:torrent|torrents)/\d", path):
        return True

    # Gazelle: torrents.php?id=4937&torrentid=12345 (or ?torrentid=12345)
    return bool(re.fullmatch(r"/?torrents\.php", path, re.IGNORECASE) and url_query(href).get("torrentid"))


def element_classes(element):
    classes = element.get("class") or []
    if isinstance(classes, str):
        classes = classes.split()
    return {str(value).casefold() for value in classes}


def find_torrent_tables(soup):
    tables = []
    for table in soup.find_all("table"):
        if is_grouped_table(table):
            tables.append(table)
            continue

        rows = table.find_all("tr")
        has_torrent_rows = any(
            "torrent_row" in element_classes(row)
            or row.select_one(".torrent-file")
            or row.select_one("a.torrent-filename, a.torrent-link")
            for row in rows
        )
        if has_torrent_rows:
            tables.append(table)
            continue

        headers = [header_label(cell) for cell in header_cells(table)]
        has_size = any("size" in header for header in headers)
        has_peers = any(
            header in {"s", "l"} or "seed" in header or "leech" in header for header in headers
        )
        has_detail_link = any(is_torrent_detail_link(anchor["href"]) for anchor in table.find_all("a", href=True))
        if has_size and has_peers and has_detail_link:
            tables.append(table)
    return tables


def is_details_row(row):
    return "torrentdetails" in element_classes(row)


def is_colhead_row(row):
    return any("colhead" in value for value in element_classes(row))


def table_rows(table):
    # Grouped listings use one tbody per type, so read every tbody rather than
    # just the first one.
    bodies = table.find_all("tbody") or [table]
    rows = [
        row
        for body in bodies
        for row in body.find_all("tr")
        if row.find_parent("table") is table
        and row.find("td", recursive=False)
        and not is_details_row(row)
        and not is_colhead_row(row)
    ]
    torrent_rows = [row for row in rows if "torrent_row" in element_classes(row)]
    return torrent_rows or rows


def associated_details_row(row):
    """Return the .torrentdetails row that expands this torrent row, if any."""
    sibling = row.find_next_sibling("tr")
    if sibling is not None and is_details_row(sibling):
        return sibling
    return None


def absolute_url(href, base_url=None):
    if not href:
        return None
    if base_url and base_url.startswith(("http://", "https://")):
        return urljoin(base_url, href)
    return href


def detail_url_from_row(row, base_url=None, columns=None):
    # The filename anchor is the canonical detail link, even if the site
    # changes its URL shape (eg. /t/123 instead of /torrent/123).
    anchor = row.select_one("a.torrent-filename[href], a.torrent-link[href]")
    if anchor is not None:
        return absolute_url(anchor["href"], base_url)

    filename_cell = get_cell(row, (columns or {}).get("filename"))
    if filename_cell is not None:
        anchors = filename_cell.find_all("a", href=True)
        for anchor in anchors:
            if is_torrent_detail_link(anchor["href"]):
                return absolute_url(anchor["href"], base_url)
        for anchor in anchors:
            if not is_download_href(anchor["href"]):
                return absolute_url(anchor["href"], base_url)

    for anchor in row.find_all("a", href=True):
        if is_torrent_detail_link(anchor["href"]):
            return absolute_url(anchor["href"], base_url)
    return None


def row_download_url(row, columns=None, base_url=None):
    anchors = []
    download_cell = get_cell(row, (columns or {}).get("download"))
    if download_cell is not None:
        anchors.extend(download_cell.find_all("a", href=True))
    anchors.extend(row.find_all("a", href=True))
    details = associated_details_row(row)
    if details is not None:
        anchors.extend(details.find_all("a", href=True))

    for anchor in anchors:
        if is_download_href(anchor["href"]):
            return absolute_url(anchor["href"], base_url)
    return None


def row_title(row, columns=None):
    anchor = row.select_one("a.torrent-filename, a.torrent-link")
    if anchor is not None:
        return anchor.get_text(" ", strip=True)

    filename_cell = get_cell(row, (columns or {}).get("filename"))
    if filename_cell is not None:
        anchors = filename_cell.find_all("a", href=True)
        for anchor in anchors:
            if is_torrent_detail_link(anchor["href"]) and anchor.get_text(" ", strip=True):
                return anchor.get_text(" ", strip=True)
        text = filename_cell.get_text(" ", strip=True)
        if text:
            return text
    return row.get_text(" ", strip=True)


def torrent_id_from_url(url):
    match = re.search(r"/(?:torrent|torrents)/(\d+)", urlparse(url or "").path)
    if match:
        return match.group(1)

    query = url_query(url)
    for key in ("torrentid", "id"):
        values = query.get(key)
        if values and values[0].isdigit():
            return values[0]
    return None


def candidate_uses_direct_download(candidate):
    if not candidate.download_url:
        return False
    if is_action_download(candidate.download_url):
        return True
    detail_path = urlparse(candidate.url).path
    download_path = urlparse(candidate.download_url).path
    if re.match(r"^/torrents/download/\d+", download_path):
        return True
    return bool(re.match(r"^/torrents/\d+", detail_path) and download_path.endswith("/download"))


def direct_download_filename(candidate):
    torrent_id = (url_query(candidate.url).get("torrentid") or [None])[0]
    if torrent_id is None:
        match = re.search(r"/(?:torrent|torrents)/(\d+)", urlparse(candidate.url).path)
        torrent_id = match.group(1) if match else None
    torrent_id = torrent_id or torrent_id_from_url(candidate.download_url)
    prefix = f"{torrent_id} - " if torrent_id else ""
    return path_utils.clean_path(f"{prefix}{candidate.title}.torrent".encode(), max_name_len=255)


def action_download_filename(details, torrent_url):
    """Name a Gazelle ?action=download response after its torrent, not torrents.php."""
    if not is_action_download(details.download_url or ""):
        return None

    torrent_id = torrent_id_from_url(details.download_url) or torrent_id_from_url(torrent_url)
    title = details.title.strip()
    if not torrent_id and not title:
        return None

    prefix = f"{torrent_id} - " if torrent_id else ""
    suffix = title or "torrent"
    return path_utils.clean_path(f"{prefix}{suffix}.torrent".encode(), max_name_len=255)


def has_horror_tag(element):
    if element is None:
        return False
    return any("taglist=horror" in (anchor.get("href") or "").casefold() for anchor in element.find_all("a", href=True))


def activity_link(activity, predicate):
    anchors = activity.find_all("a", href=True)
    for anchor in anchors:
        if predicate(anchor["href"]):
            return anchor
    return None


def activity_info_candidates(soup, base_url=None):
    """Parse the card layout used by some group pages (.activity_info rows)."""
    candidates = []
    for activity in soup.select(".activity_info"):
        card = activity.find_parent(class_="torrent_card")
        anchor = activity_link(activity, is_torrent_detail_link)
        if anchor is None and card is not None:
            anchor = activity_link(card, is_torrent_detail_link)
        if anchor is None:
            continue

        download_anchor = activity_link(activity, is_download_href)
        if download_anchor is None and card is not None:
            download_anchor = activity_link(card, is_download_href)

        children = activity.find_all("div", recursive=False)
        size_cell = children[1] if len(children) > 1 else activity.select_one("div:nth-child(2)")
        size_mb = parse_size(size_cell.get_text(" ", strip=True)) / (1024**2) if size_cell is not None else 0

        seed_element = activity.select_one(".torrent_seed b")
        seeders = first_int(seed_element.get_text()) if seed_element is not None else 0
        snatched_element = activity.select_one(".torrent_snatched b")
        completed = first_int(snatched_element.get_text()) if snatched_element is not None else 0

        title = anchor.get_text(" ", strip=True) or activity.get_text(" ", strip=True)
        candidates.append(
            TorrentCandidate(
                url=absolute_url(anchor["href"], base_url),
                title=title,
                row=activity,
                columns={},
                score=qualitative_score(
                    seeders=seeders,
                    completed=completed,
                    size_mb=size_mb,
                    free=1 if has_free_download(activity) else 0,
                    resolution_rank=get_resolution_rank(activity),
                ),
                seeders=seeders,
                has_english_subtitles=has_english_subtitles(activity),
                download_url=absolute_url(download_anchor["href"], base_url) if download_anchor is not None else None,
                is_horror=has_horror_tag(activity) or has_horror_tag(card),
            )
        )
    return candidates


def torrent_candidates(soup, base_url=None):
    """Return every torrent candidate across detected listing layouts, including horror ones."""
    tables = find_torrent_tables(soup)
    log.debug("Found %d torrent table(s)", len(tables))

    table_candidates = []
    for table in tables:
        columns = build_column_map(table)
        for row in table_rows(table):
            url = detail_url_from_row(row, base_url, columns)
            if not url:
                continue
            table_candidates.append(
                TorrentCandidate(
                    url=url,
                    title=row_title(row, columns),
                    row=row,
                    columns=columns,
                    score=get_qualitative_score(row, columns),
                    seeders=get_seeders(row, columns),
                    has_english_subtitles=has_english_subtitles(row),
                    download_url=row_download_url(row, columns, base_url),
                    is_horror=has_horror_tag(row),
                )
            )

    card_candidates = activity_info_candidates(soup, base_url)
    log.debug("Found %d activity_info torrent card(s)", len(card_candidates))

    # Some themes render both layouts; keep one candidate per torrent.
    by_url = {}
    for candidate in table_candidates + card_candidates:
        key = candidate.url.split("#", 1)[0]
        existing = by_url.get(key)
        if existing is None or (candidate.download_url and not existing.download_url):
            by_url[key] = candidate
    return list(by_url.values())


def best_from_candidates(candidates):
    candidates = [candidate for candidate in candidates if not candidate.is_horror]
    if not candidates:
        return None
    return max(candidates, key=lambda c: (c.seeders > 0, c.has_english_subtitles, c.score))


def report_horror_torrents(candidates):
    urls = list(dict.fromkeys(candidate.url for candidate in candidates if candidate.is_horror))
    for url in urls:
        print(f"Horror: {url}", file=sys.stderr)
    return urls


def best_torrent_from_soup(soup, base_url=None):
    """Return the highest-ranked non-horror torrent across every detected listing layout."""
    candidates = torrent_candidates(soup, base_url)
    if not candidates:
        log.debug("Found %d torrent row(s) without a usable detail URL", len(soup.select(".torrent-file, .torrent_row")))
        return None
    return best_from_candidates(candidates)


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
    if find_details_table(soup) is not None:
        return True

    # A group page can contain download links too; its listing content wins.
    if find_torrent_tables(soup) or soup.select_one(".activity_info, .grouped_info, .torrent_card"):
        return False

    # Gazelle detail pages have no details table, but expose action=download.
    return any(is_action_download(anchor["href"]) for anchor in soup.find_all("a", href=True))


def is_torrent_url(url):
    return url.startswith(("http://", "https://")) and is_torrent_detail_link(url)


def is_torrents_url(url):
    return url.startswith(("http://", "https://")) and bool(re.fullmatch(r"/torrents/\d+/?", urlparse(url).path))


def direct_torrents_download_urls(url):
    """Return download links for a bare /torrents/<id> page, including the
    reversed /torrents/download/<id> form used by some sites."""
    base = url.rstrip("/")
    urls = [base + "/download"]
    torrent_id = torrent_id_from_url(base)
    if torrent_id:
        parsed = urlparse(base)
        reversed_path = f"/torrents/download/{torrent_id}"
        reversed_url = parsed._replace(path=reversed_path, query="", fragment="").geturl()
        if reversed_url not in urls:
            urls.append(reversed_url)
    return urls


def direct_torrents_filename(url):
    match = re.search(r"/torrents/(\d+)", urlparse(url).path)
    return f"{match.group(1) if match else 'torrent'}.torrent"


def is_listing_url(url):
    return bool(re.search(r"/(?:movie|movies|tv|series|manga|mangas|anime|animes)/", urlparse(url).path, re.IGNORECASE))


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


def action_download_url(soup, base_url=None):
    """Find a Gazelle-style ?action=download link, preferring the URL's torrent id."""
    anchors = [
        anchor
        for anchor in soup.find_all("a", href=True)
        if is_action_download(anchor["href"]) and "/download/subtitle/" not in anchor["href"]
    ]
    if not anchors:
        return None

    wanted = torrent_id_from_url(base_url)
    if wanted:
        for anchor in anchors:
            if torrent_id_from_url(anchor["href"]) == wanted:
                return anchor["href"]
    return anchors[0]["href"]


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
        torrent_url = action_download_url(soup, base_url)
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
# Rate limiting and pacing
# ============================================================================


def pace_links(args):
    seconds = getattr(args, "sleep_links", 0) or 0
    last = getattr(args, "_last_link_finished", None)
    if seconds <= 0 or last is None:
        return

    delay = seconds - (time.monotonic() - last)
    if delay > 0:
        time.sleep(delay)


def mark_link_finished(args):
    args._last_link_finished = time.monotonic()


def is_stop_error(excinfo):
    if isinstance(excinfo, HTTPTooManyRequestsError):
        return True

    response = getattr(excinfo, "response", None)
    if getattr(response, "status_code", None) in BLOCKED_STATUSES:
        return True

    return bool(re.search(r"\bHTTP(?:403|429)\b", str(excinfo)))


def html_looks_blocked(html):
    if not html:
        return False
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    text = (match.group(1) if match else html[:2000]).strip()
    return bool(
        re.search(
            r"too many requests|rate limit|access denied|just a moment|attention required|checking your browser",
            text,
            re.IGNORECASE,
        )
        or re.match(r"^\s*(?:403|429)\b", text)
    )


def add_remaining(state, torrent_url):
    if torrent_url and torrent_url not in state.remaining_torrent_urls:
        state.remaining_torrent_urls.append(torrent_url)


def state_blocked(state):
    return state.network_stopped or state.downloads_blocked


def torrent_list_files(base_dir=None):
    root = Path(base_dir).expanduser() if base_dir else TORRENT_LIST_ROOT.expanduser()
    return sorted(root.glob("*.list"))


def read_torrent_list(path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def save_torrent_list(path, links):
    if links:
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text("\n".join(links) + "\n", encoding="utf-8")
        temporary.replace(path)
        log.info("Kept %d unprocessed link(s) in %s", len(links), path)
    elif path.exists():
        path.unlink()
        log.info("Removed empty %s", path)


def process_torrent_lists(args, state):
    files = torrent_list_files()
    if not files:
        log.warning("No .list files found in %s", TORRENT_LIST_ROOT.expanduser())
        return

    for path in files:
        links = read_torrent_list(path)
        if not links:
            save_torrent_list(path, links)
            continue

        # Each file is a single domain, so a 429/403 only blocks this file.
        domain_state = RunState()
        log.info("Processing %d link(s) from %s", len(links), path)

        remaining = list(links)
        try:
            for index, url in enumerate(links):
                if state_blocked(domain_state):
                    remaining = links[index:]
                    break

                # Keep the current link unless it is handled, so a failure or
                # Ctrl-C during processing leaves it queued.
                remaining = links[index:]
                if process_url(args, url, domain_state):
                    remaining = links[index + 1 :]
                elif state_blocked(domain_state):
                    break
        finally:
            save_torrent_list(path, remaining)
            state.torrents_downloaded += domain_state.torrents_downloaded

        if state_blocked(domain_state):
            log.warning("HTTP 429/403 on this domain; continuing with the next .list file")


def torrent_list_path(url, base_dir=None):
    domain = urlparse(url).hostname or "unknown"
    root = Path(base_dir).expanduser() if base_dir else TORRENT_LIST_ROOT.expanduser()
    return root / f"{domain}.list"


def save_remaining_torrents(urls, base_dir=None):
    by_domain = {}
    for url in urls:
        by_domain.setdefault((urlparse(url).hostname or "unknown"), []).append(url)

    written = []
    for links in by_domain.values():
        path = torrent_list_path(links[0], base_dir)
        path.parent.mkdir(parents=True, exist_ok=True)

        existing_text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        existing = set(existing_text.splitlines())
        new_links = [link for link in links if link not in existing]
        if not new_links:
            continue

        with path.open("a", encoding="utf-8") as file:
            if existing_text and not existing_text.endswith("\n"):
                file.write("\n")
            for link in new_links:
                file.write(f"{link}\n")

        log.warning("Saved %d remaining torrent link(s) to %s", len(new_links), path)
        written.append(path)

    return written


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
                By.CSS_SELECTOR,
                '.torrent-file, a.torrent-filename, a.torrent-link, .torrent_row, .activity_info,'
                ' a[href*="action=download"], a[href*="/download/torrent/"], a[href$="/download"]',
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
        pace_links(args)
        try:
            web.selenium_get_page(args, url)
            wait_for_selenium_content(args)
            html = args.driver.page_source
        finally:
            mark_link_finished(args)
    else:
        pace_links(args)
        try:
            response = web.get(args, url)
            html = response.text if response is not None else None
        finally:
            mark_link_finished(args)

    if html_looks_blocked(html):
        raise HTTPTooManyRequestsError(f"HTTP 429/403 block page: {url}")

    log.debug("Fetched %s bytes from %s", len(html) if html else 0, url)
    return html


def filename_from_url(url):
    filename = Path(unquote(urlparse(url).path)).name or "download"
    return path_utils.clean_path(filename.encode(), max_name_len=255)


def download_file(args, url, output_name=None):
    destination = Path(args.prefix).expanduser()
    destination.mkdir(parents=True, exist_ok=True)
    output_path = destination / (output_name or filename_from_url(url))
    pace_links(args)
    try:
        return web.download_url(args, url, str(output_path))
    finally:
        mark_link_finished(args)


def download_selected(args, torrent_url, details, state, output_name=None, has_subtitle_info=True):
    """Download the .torrent (and subtitle); return False only if a 429/403 blocked it."""
    if not details.download_url:
        log.warning("Could not find a download link on %s", torrent_url)
        return False

    try:
        downloaded = download_file(args, details.download_url, output_name=output_name)
    except Exception as excinfo:
        if not is_stop_error(excinfo):
            raise
        state.downloads_blocked = True
        add_remaining(state, torrent_url)
        log.warning("HTTP 429/403 while downloading %s; disabling downloads and finishing evaluation", torrent_url)
        return False

    if downloaded:
        print(downloaded)
        state.torrents_downloaded += 1

    if not details.subtitle_url:
        if has_subtitle_info:
            log.info("No downloadable English subtitle found on %s", torrent_url)
        return True

    try:
        downloaded = download_file(args, details.subtitle_url)
    except Exception as excinfo:
        if not is_stop_error(excinfo):
            raise
        state.downloads_blocked = True
        add_remaining(state, torrent_url)
        log.warning("HTTP 429/403 while downloading the subtitle for %s; disabling downloads", torrent_url)
        return True

    if downloaded:
        print(downloaded)
    return True


def download_direct_torrents(args, torrent_url, state):
    """Download a bare /torrents/<id> page, trying each known download URL shape."""
    for download_url in direct_torrents_download_urls(torrent_url):
        details = TorrentPage(
            title="",
            download_url=download_url,
            subtitle_url=None,
            subtitle_age_years=None,
            is_english_subtitle=False,
        )
        try:
            return download_selected(
                args,
                torrent_url,
                details,
                state,
                output_name=direct_torrents_filename(torrent_url),
                has_subtitle_info=False,
            )
        except UnrecoverableError as excinfo:
            if "HTTP404" not in str(excinfo):
                raise
            log.debug("No torrent at %s (%s); trying the next download URL shape", download_url, excinfo)
    return False


def process_url(args, url, state=None):
    """Process one URL; return False when it should stay queued (blocked or not downloaded)."""
    state = state or RunState()

    if state.network_stopped and not getattr(args, "local_html", False):
        if is_torrent_url(url) or is_torrents_url(url):
            add_remaining(state, url)
            log.warning("Queued %s (network stopped after HTTP 429/403)", url)
        else:
            log.warning("Skipping %s: network stopped after HTTP 429/403", url)
        return False

    if is_torrents_url(url) and not getattr(args, "local_html", False):
        torrent_url = url.rstrip("/")
        if getattr(args, "select_only", False):
            print(torrent_url)
            return True
        if state.downloads_blocked:
            add_remaining(state, torrent_url)
            log.warning("Downloads disabled after HTTP 429/403; queued %s", torrent_url)
            return False
        return download_direct_torrents(args, torrent_url, state)

    direct_torrent_url = is_torrent_url(url)

    try:
        html = fetch_html(args, url)
    except Exception as excinfo:
        if not is_stop_error(excinfo):
            raise
        state.downloads_blocked = True
        state.network_stopped = True
        if direct_torrent_url:
            add_remaining(state, url)
            log.warning("HTTP 429/403 while fetching %s; queued it and stopping network requests", url)
        else:
            log.warning("HTTP 429/403 while fetching %s; stopping network requests", url)
        return False

    if not html:
        log.warning("Could not get a response for %s", url)
        return False

    soup = BeautifulSoup(html, "html.parser")
    base_url = None if getattr(args, "local_html", False) else url

    if direct_torrent_url or (is_torrent_detail_page(soup) and not is_listing_url(url)):
        torrent_url = url
        if getattr(args, "select_only", False):
            print(torrent_url)
            return True
        if state.downloads_blocked:
            add_remaining(state, torrent_url)
            log.warning("Downloads disabled after HTTP 429/403; queued %s", torrent_url)
            return False
        details = parse_torrent_page(soup, base_url)
        return download_selected(
            args,
            torrent_url,
            details,
            state,
            output_name=action_download_filename(details, torrent_url),
        )

    candidates = torrent_candidates(soup, base_url)
    horror_urls = report_horror_torrents(candidates)
    candidate = best_from_candidates(candidates)
    if candidate is None:
        if horror_urls:
            log.warning("Skipped %d horror torrent(s) in %s; no non-horror torrent selected", len(horror_urls), url)
            return True
        if find_torrent_tables(soup):
            log.warning("Found torrent table(s) in %s, but no rows had a usable detail link", url)
        else:
            log.warning(
                "Could not find any torrent rows in %s (try a larger --wait if the page loads them dynamically)",
                url,
            )
        return False

    torrent_url = candidate.url
    if getattr(args, "select_only", False):
        print(torrent_url)
        return True

    log.info("Selected %s (%s seeders, score %.3f)", candidate.title, candidate.seeders, candidate.score)

    if state.downloads_blocked:
        add_remaining(state, torrent_url)
        log.warning("Downloads disabled after HTTP 429/403; queued %s", torrent_url)
        return False

    if candidate_uses_direct_download(candidate):
        details = TorrentPage(
            title=candidate.title,
            download_url=candidate.download_url,
            subtitle_url=None,
            subtitle_age_years=None,
            is_english_subtitle=False,
        )
        return download_selected(
            args,
            torrent_url,
            details,
            state,
            output_name=direct_download_filename(candidate),
            has_subtitle_info=False,
        )

    try:
        torrent_html = fetch_html(args, torrent_url)
    except Exception as excinfo:
        if not is_stop_error(excinfo):
            raise
        state.downloads_blocked = True
        state.network_stopped = True
        add_remaining(state, torrent_url)
        log.warning("HTTP 429/403 while fetching %s; queued it and stopping network requests", torrent_url)
        return False

    if not torrent_html:
        log.warning("Could not get a response for %s", torrent_url)
        return False

    details = parse_torrent_page(BeautifulSoup(torrent_html, "html.parser"), torrent_url)
    return download_selected(args, torrent_url, details, state)


def print_download_summary(state):
    sys.stdout.flush()
    print(f"Total .torrent files downloaded: {state.torrents_downloaded}", file=sys.stderr)


def main():
    args = parse_args()
    state = RunState()

    try:
        if getattr(args, "drain_backlog", False):
            process_torrent_lists(args, state)
        else:
            for url in shell_utils.gen_paths(args):
                process_url(args, url, state)
    finally:
        try:
            if state.remaining_torrent_urls:
                save_remaining_torrents(state.remaining_torrent_urls)
        finally:
            print_download_summary(state)
            if getattr(args, "selenium", False) and getattr(args, "driver", None):
                web.quit_selenium(args)


if __name__ == "__main__":
    sys.exit(main())
