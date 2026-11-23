#!/usr/bin/python3
"""Pick the best direct-download release from a download page and fetch it.

Pages sometimes hide their download links behind a "Show Links" button.
Selenium (with --cookies-from-browser) is used to reveal those links, then the page is parsed like a listing table:

* English releases are preferred over other languages.
* GDI is preferred over CDI when both are offered.
* When several English releases exist, the most recent one is selected.
* Every disc/part belonging to the selected release is downloaded.
* Supplementary files (manuals, PDFs, text files, soundtracks, and files whose
  size is significantly different from the main release) are downloaded too,
  unless they are CDI images.

Downloads are sequential and paced with --sleep-links (default: 3 seconds).
On HTTP 429 or 403 the run stops downloading and queues the remaining page
URLs in ~/.local/data/directdownload.best/$domain.list. With --drain-backlog
those lists are replayed instead of the positional URLs.

Files are written to --out-dir (alias of --prefix; default ~/Downloads) using
the layout $prefix/$domain/$page/$existing_name.
"""

import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse

from bs4 import BeautifulSoup
from library.data.http_errors import HTTPTooManyRequestsError
from library.utils import arggroups, argparse_utils, path_utils, shell_utils, web
from library.utils.log_utils import log

DEFAULT_SLEEP_LINKS = 3.0
DEFAULT_SELECTOR = "#acf-content-wrapper, #download, .download-links, .entry-content"
DIRECT_LIST_ROOT = Path("~/.local/data/directdownload.best")
BLOCKED_STATUSES = {403, 429}

# Links loaded by the site's "Show Links" button.
REVEALED_LINK_SELECTOR = (
    ".download-links a[href], a[id^='dl-btn-'], #acf-content-wrapper [data-href]"
)

SIZE_UNITS = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}

AGE_UNITS = [
    (r"(\d+(?:\.\d+)?)\s*years?", 365),
    (r"(\d+(?:\.\d+)?)\s*months?", 30),
    (r"(\d+(?:\.\d+)?)\s*weeks?", 7),
    (r"(\d+(?:\.\d+)?)\s*days?", 1),
    (r"(\d+(?:\.\d+)?)\s*hours?", 1 / 24),
    (r"(\d+(?:\.\d+)?)\s*minutes?", 1 / 1440),
]

GAME_FORMATS = {"gdi", "cdi", "iso", "chd", "bin", "cue", "rom", "zip", "7z", "rar"}
FORMAT_RANK = {
    "gdi": 0,
    "iso": 1,
    "chd": 2,
    "bin": 3,
    "rom": 4,
    "zip": 5,
    "7z": 6,
    "rar": 7,
    "cdi": 99,
}

DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".doc",
    ".docx",
    ".rtf",
    ".nfo",
    ".md",
    ".csv",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".mp3",
    ".flac",
    ".ogg",
    ".wav",
    ".mp4",
    ".mkv",
    ".avi",
}

SUPPLEMENTARY_WORDS = re.compile(
    r"\b(manual|guide|artbook|art book|soundtrack|ost|bonus|extra|patch|readme|nfo|"
    r"cheat|map|document|scan|cover|box ?art|instruction|dlc)\b",
    re.IGNORECASE,
)

TITLE_STOPWORDS = {
    "and",
    "available",
    "beta",
    "disc",
    "dlc",
    "download",
    "english",
    "eur",
    "europe",
    "for",
    "here",
    "iso",
    "japan",
    "japanese",
    "mtl",
    "part",
    "patched",
    "rom",
    "series",
    "the",
    "usa",
    "version",
    "vol",
    "volume",
    "with",
}

PART_PATTERN = re.compile(
    r"\b(?:disc|disk|cd|part|volume|vol)\s*[-_ ]?(\d+)\b", re.IGNORECASE
)


@dataclass
class DownloadLink:
    url: str
    label: str
    context: str
    order: int
    format: str = ""
    language: str = ""
    part: str = ""
    size_bytes: int = 0
    age_years: float | None = None
    date_text: str = ""
    host: str = ""

    @property
    def is_english(self):
        return self.language == "english"

    @property
    def is_cdi(self):
        return self.format == "cdi"

    @property
    def is_game(self):
        return self.format in GAME_FORMATS or bool(
            re.search(r"\b(game|rom|iso)\b", self.label, re.IGNORECASE)
        )

    @property
    def release_key(self):
        # Host is deliberately omitted: parts of one release are often spread
        # across the site's mirror subdomains (raziel, alucard, sydney, ...).
        base = normalize_label(re.sub(PART_PATTERN, "", f"{self.label} {self.context}"))
        if not base:
            base = urlparse(self.url).path
        return (self.language, self.format, base)


@dataclass
class DownloadPage:
    title: str
    links: list[DownloadLink]


@dataclass
class RunState:
    downloads_blocked: bool = False
    network_stopped: bool = False
    remaining_page_urls: list[str] = field(default_factory=list)
    visited_urls: set[str] = field(default_factory=set)
    files_downloaded: int = 0


def parse_args():
    parser = argparse_utils.ArgumentParser(description=__doc__)

    arggroups.requests(parser)
    arggroups.download(parser, profile=False, safe=False)
    arggroups.selenium(parser)
    parser.add_argument(
        "--no-selenium",
        dest="selenium",
        action="store_false",
        help="Use plain HTTP requests instead of Selenium (links already expanded only)",
    )
    parser.set_defaults(
        selenium=True, cookies_from_browser="firefox", prefix="~/Downloads"
    )

    parser.add_argument(
        "--out-dir",
        dest="prefix",
        metavar="DIR",
        help="Directory to write downloads to (alias of --prefix; default: ~/Downloads)",
    )
    parser.add_argument(
        "--local-html",
        action="store_true",
        help="Treat positional paths as local HTML files instead of URLs",
    )
    parser.add_argument(
        "--select-only",
        action="store_true",
        help="Only print the selected download URLs; do not download",
    )
    parser.add_argument(
        "--drain-backlog",
        "--backlog",
        dest="drain_backlog",
        action="store_true",
        help="Process every .list file in ~/.local/data/directdownload.best/ and remove handled URLs",
    )
    parser.add_argument(
        "--wait",
        type=float,
        default=10,
        metavar="SECONDS",
        help="When using Selenium, wait up to N seconds for the revealed links",
    )
    parser.add_argument(
        "--sleep-links",
        type=float,
        default=DEFAULT_SLEEP_LINKS,
        metavar="SECONDS",
        help="Sleep N seconds between each page fetch or download (default: 3)",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        metavar="N",
        help="Follow nested download pages (eg. DLC pages) up to N levels deep (default: 2)",
    )
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser, required=False)
    args = parser.parse_intermixed_args()

    if getattr(args, "drain_backlog", False):
        if args.paths:
            log.warning(
                "Ignoring positional paths because --drain-backlog reads the .list files"
            )
    elif args.paths is None:
        args.paths = argparse_utils.read_stdin(parser.prog)

    if args.local_html:
        args.selenium = False
    arggroups.args_post(args, parser)

    web.requests_session(args)
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
                status_forcelist=[
                    status for status in retry.status_forcelist if status != 429
                ]
            )


# ============================================================================
# Link parsing
# ============================================================================


def normalize_label(text):
    return re.sub(r"\s+", " ", (text or "")).strip().casefold()


def element_text(element):
    return element.get_text(" ", strip=True) if element is not None else ""


def parse_size_bytes(size_string):
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*([KMGT]?)i?B\b", size_string or "", re.IGNORECASE
    )
    if not match:
        return 0
    return int(float(match.group(1)) * SIZE_UNITS.get(match.group(2).upper() + "B", 1))


def age_years_from_text(text):
    text = (text or "").lower()
    total_days = 0.0
    matched = False
    for pattern, days_per_unit in AGE_UNITS:
        for match in re.finditer(pattern, text):
            total_days += float(match.group(1)) * days_per_unit
            matched = True
    return total_days / 365 if matched else None


def detect_language(text):
    text = (text or "").casefold()
    if re.search(r"\b(english|eng|en)\b", text):
        return "english"
    if re.search(r"\b(japanese|japan|jpn|jp|ntsc-j)\b", text):
        return "japanese"
    if re.search(r"\b(europe|eur|pal)\b", text):
        return "europe"
    if re.search(r"\b(usa|us|ntsc-u)\b", text):
        return "usa"
    return ""


def detect_format(text, url=""):
    # Only the URL's basename is inspected; directory words such as "psx-iso"
    # or "sega_saturn_isos" must not make every link look like an ISO.
    basename = Path(unquote(urlparse(url).path)).name
    haystack = f"{text or ''} {basename}".casefold()
    path_extension = Path(basename).suffix.casefold().lstrip(".")

    for fmt in ("gdi", "cdi", "chd", "iso"):
        if re.search(rf"\b{fmt}\b", haystack) or path_extension == fmt:
            return fmt
    if re.search(
        r"\b(bin\s*/?\s*cue|bin&cue|bin/cue)\b", haystack
    ) or path_extension in {"bin", "cue"}:
        return "bin"
    if re.search(r"\brom\b", haystack):
        return "rom"
    for fmt in ("zip", "7z", "rar"):
        if path_extension == fmt:
            return fmt
    return ""


def detect_part(text):
    match = PART_PATTERN.search(text or "")
    return match.group(0).casefold() if match else ""


def is_supplementary_label(text):
    return bool(SUPPLEMENTARY_WORDS.search(text or ""))


def is_supplementary_url(url):
    extension = Path(unquote(urlparse(url).path)).suffix.casefold()
    return extension in DOCUMENT_EXTENSIONS


NOISE_LINK_PATTERN = re.compile(
    r"(report-issue|report outdated|disqus\.com|ko-fi\.com|/login/|/register/)",
    re.IGNORECASE,
)


def is_file_url(url):
    if not url.startswith(("http://", "https://")):
        return False
    path = urlparse(url).path
    if path.endswith("/download.php"):
        return True
    extension = Path(unquote(path)).suffix.casefold()
    return bool(extension) and extension not in {
        ".html",
        ".htm",
        ".php",
        ".asp",
        ".aspx",
    }


def is_download_page_url(url):
    if not url.startswith(("http://", "https://")):
        return False
    return "/repo/" in urlparse(url).path and not is_file_url(url)


def anchor_url(anchor):
    for attribute in ("href", "data-href", "data-url", "data-link", "data-download"):
        value = (anchor.get(attribute) or "").strip()
        if value and not value.startswith(("#", "javascript:", "mailto:")):
            return value
    return None


def nearest_heading(start, scope):
    """Return the closest preceding heading/label text within a scope."""
    for element in start.find_all_previous(
        ["h1", "h2", "h3", "h4", "h5", "h6", "strong", "b", "legend"]
    ):
        if scope is not None and scope not in element.parents and element is not scope:
            continue
        text = element_text(element)
        if text:
            return text
    return ""


def link_container(anchor, container):
    """Return the smallest ancestor that describes just this link's row."""
    row_tokens = {"row", "tr", "item", "entry", "release", "version", "dl-main"}
    node = anchor
    while node is not None and node is not container:
        classes = {str(value).casefold() for value in node.get("class") or []}
        if node.name == "tr" or classes & row_tokens:
            text = element_text(node)
            if text and len(text) <= 500:
                return node
        node = node.parent
    return anchor.parent


def download_container(soup):
    """Return the element holding download rows, ignoring empty duplicate wrappers."""
    wrappers = soup.select("#acf-content-wrapper")
    if wrappers:
        wrapper = max(wrappers, key=lambda node: len(node.find_all("a", href=True)))
        return wrapper.select_one(".download-links") or wrapper

    for selector in (
        "#download .download-links",
        ".download-links",
        "#download",
        DEFAULT_SELECTOR,
    ):
        container = soup.select_one(selector)
        if container is not None and container.find("a", href=True):
            return container
    return soup.body or soup


def collect_download_links(soup, base_url=None):
    container = download_container(soup)
    scope = container.find_parent(id="download") or container.parent or container

    links = []
    seen = set()
    for index, anchor in enumerate(container.find_all("a", recursive=True)):
        href = anchor_url(anchor)
        if not href:
            continue
        if NOISE_LINK_PATTERN.search(f"{href} {element_text(anchor)}"):
            continue
        url = urljoin(base_url, href) if base_url else href
        if url in seen:
            continue
        seen.add(url)

        row = link_container(anchor, container)
        row_text = element_text(row)
        anchor_text = element_text(anchor)
        label = anchor_text or row_text
        if label.casefold() in {"download", "downloads", "here", "link", "show links"}:
            label = row_text
        context = nearest_heading(row, scope)
        row_combined = f"{label} {row_text}"

        row_age = age_years_from_text(row_text)
        context_age = age_years_from_text(context)
        # Row-level badges ("English v1.3", "Japan", "[GDI]") win over the
        # page-level heading, which may mention both languages and formats.
        format_name = detect_format(row_combined, url) or detect_format(context, url)
        language = detect_language(row_combined) or detect_language(context)
        links.append(
            DownloadLink(
                url=url,
                label=label,
                context=context,
                order=index,
                format=format_name,
                language=language,
                part=detect_part(row_combined),
                size_bytes=parse_size_bytes(row_text) or parse_size_bytes(context),
                age_years=row_age if row_age is not None else context_age,
                date_text=row_text if row_age is not None else context,
                host=urlparse(url).hostname or "",
            )
        )
    return links


def page_title(soup):
    for selector in (
        "h1.entry-title",
        "#download h2.entry-title",
        "#download h2",
        "h1",
        "title",
    ):
        element = soup.select_one(selector)
        text = element_text(element)
        if text:
            return re.sub(r"^download:\s*", "", text, flags=re.IGNORECASE).strip()
    return ""


def parse_download_page(soup, base_url=None):
    title = page_title(soup)
    links = collect_download_links(soup, base_url)
    if not title:
        title = "download"
    return DownloadPage(title=title, links=links)


def page_is_english(page):
    return detect_language(page.title) == "english" or bool(
        re.search(r"\benglish\b", page.title, re.IGNORECASE)
    )


def group_releases(links):
    groups = {}
    for link in links:
        groups.setdefault(link.release_key, []).append(link)
    return list(groups.values())


def version_tuple(text):
    versions = re.findall(r"\bv?(\d+(?:\.\d+)+)\b", (text or "").casefold())
    if not versions:
        return ()
    return max(tuple(int(part) for part in version.split(".")) for version in versions)


def group_rank(group):
    first = group[0]
    newest = min(
        (link.age_years for link in group if link.age_years is not None),
        default=float("inf"),
    )
    # Higher versions are more recent than lower ones when no upload date is
    # shown: negate the tuple so min() picks the highest version first.
    version = version_tuple(f"{first.label} {first.context}")
    version_rank = tuple(-part for part in version) if version else (1,)
    return (
        0 if any(link.is_english for link in group) else 1,
        FORMAT_RANK.get(first.format, 50),
        version_rank,
        newest,
        first.order,
    )


def significant_words(title):
    return {
        word
        for word in re.findall(r"[a-z0-9]{4,}", (title or "").casefold())
        if word not in TITLE_STOPWORDS
    }


def is_listing_page(page):
    """A page linking to many other /repo/ pages is an index, not one release."""
    page_links = [link for link in page.links if is_download_page_url(link.url)]
    return len(page.links) >= 20 and len(page_links) >= 10


def link_matches_words(link, words):
    # Whole tokens only: "nano" must not match a different game such as
    # "Nanoha" and send the crawler down the wrong page.
    tokens = set(
        re.findall(r"[a-z0-9]+", unquote(f"{link.label} {link.url}").casefold())
    )
    return bool(tokens & words)


def same_site(first_url, second_url):
    first_host = urlparse(first_url).hostname or ""
    second_host = urlparse(second_url).hostname or ""
    if not first_host or not second_host:
        return False
    return (
        first_host == second_host
        or first_host.endswith("." + second_host)
        or second_host.endswith("." + first_host)
    )


def select_downloads(page):
    """Return the selected links: newest English release (GDI over CDI) plus extras."""
    links = [link for link in page.links if link.url]
    if not links:
        return []

    # Explicit language markers on the links win over the page title: a page
    # titled "(English Patched)" may still list a separate Japanese release.
    marked = [link for link in links if link.language]
    english = [link for link in links if link.is_english]
    if not marked and page_is_english(page):
        english = links
    pool = english or links
    if not english:
        log.warning("No English marker found on %r; using every link", page.title)

    # GDI beats CDI when both exist for the same page.
    if any(link.format == "gdi" for link in pool):
        pool = [link for link in pool if link.format != "cdi"]

    groups = group_releases(pool)
    chosen_group = min(groups, key=group_rank)
    chosen = list(chosen_group)

    known_sizes = [link.size_bytes for link in chosen if link.size_bytes]
    main_size = max(known_sizes) if known_sizes else 0

    chosen_urls = {link.url for link in chosen}
    known_release_keys = {link.release_key for link in chosen}
    for link in links:
        if link.url in chosen_urls or link.is_cdi:
            continue
        if link.release_key in known_release_keys:
            continue
        if (
            is_supplementary_url(link.url)
            or is_supplementary_label(f"{link.label} {link.context}")
            or main_size
            and link.size_bytes
            and link.size_bytes < main_size * 0.5
        ):
            chosen.append(link)
            chosen_urls.add(link.url)

    chosen.sort(key=lambda link: link.order)
    return chosen


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


# ============================================================================
# Backlog lists
# ============================================================================


def direct_list_files(base_dir=None):
    root = Path(base_dir).expanduser() if base_dir else DIRECT_LIST_ROOT.expanduser()
    return sorted(root.glob("*.list"))


def read_link_list(path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def save_link_list(path, links):
    if links:
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text("\n".join(links) + "\n", encoding="utf-8")
        temporary.replace(path)
        log.info("Kept %d unprocessed link(s) in %s", len(links), path)
    elif path.exists():
        path.unlink()
        log.info("Removed empty %s", path)


def direct_list_path(url, base_dir=None):
    domain = urlparse(url).hostname or "unknown"
    root = Path(base_dir).expanduser() if base_dir else DIRECT_LIST_ROOT.expanduser()
    return root / f"{domain}.list"


def save_remaining_pages(urls, base_dir=None):
    by_domain = {}
    for url in urls:
        by_domain.setdefault(urlparse(url).hostname or "unknown", []).append(url)

    written = []
    for links in by_domain.values():
        path = direct_list_path(links[0], base_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        existing_text = (
            path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        )
        existing = set(existing_text.splitlines())
        new_links = [link for link in links if link not in existing]
        if not new_links:
            continue
        with path.open("a", encoding="utf-8") as file:
            if existing_text and not existing_text.endswith("\n"):
                file.write("\n")
            for link in new_links:
                file.write(f"{link}\n")
        log.warning("Saved %d remaining page link(s) to %s", len(new_links), path)
        written.append(path)
    return written


def process_direct_lists(args, state):
    files = direct_list_files()
    if not files:
        log.warning("No .list files found in %s", DIRECT_LIST_ROOT.expanduser())
        return

    for path in files:
        links = read_link_list(path)
        if not links:
            save_link_list(path, links)
            continue

        domain_state = RunState()
        log.info("Processing %d link(s) from %s", len(links), path)
        remaining = list(links)
        try:
            for index, url in enumerate(links):
                if domain_state.network_stopped or domain_state.downloads_blocked:
                    remaining = links[index:]
                    break
                remaining = links[index:]
                if process_url(args, url, domain_state):
                    remaining = links[index + 1 :]
        finally:
            save_link_list(path, remaining)
            state.files_downloaded += domain_state.files_downloaded

        if domain_state.network_stopped or domain_state.downloads_blocked:
            log.warning(
                "HTTP 429/403 on this domain; continuing with the next .list file"
            )


# ============================================================================
# Fetching and downloading
# ============================================================================


def wait_for_revealed_links(args, timeout=None):
    timeout = getattr(args, "wait", 10) if timeout is None else timeout
    if timeout <= 0:
        return bool(args.driver.find_elements("css selector", REVEALED_LINK_SELECTOR))
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait

        WebDriverWait(args.driver, timeout).until(
            lambda driver: driver.find_elements(By.CSS_SELECTOR, REVEALED_LINK_SELECTOR)
        )
        return True
    except Exception as excinfo:  # noqa: BLE001
        log.debug(
            "Download links did not appear within %s seconds: %s", timeout, excinfo
        )
        return False


def reveal_download_links(args):
    """Click every "Show Links" button and wait for the AJAX links to render."""
    if not getattr(args, "selenium", False) or not getattr(args, "driver", None):
        return

    if args.driver.find_elements("css selector", REVEALED_LINK_SELECTOR):
        return

    buttons = args.driver.find_elements("css selector", ".acf-get-content-button")
    if not buttons:
        buttons = args.driver.find_elements("css selector", "#download button")
    if not buttons:
        return

    for button in buttons:
        try:
            args.driver.execute_script("arguments[0].click();", button)
        except Exception as excinfo:  # noqa: BLE001
            log.debug("Could not click reveal button: %s", excinfo)

    # Some pages render the button before its click handler is bound, so a
    # second attempt after the AJAX window is useful.
    if not wait_for_revealed_links(args):
        time.sleep(2)
        buttons = args.driver.find_elements("css selector", ".acf-get-content-button")
        for button in buttons:
            try:
                args.driver.execute_script("arguments[0].click();", button)
            except Exception as excinfo:  # noqa: BLE001
                log.debug("Could not re-click reveal button: %s", excinfo)
        wait_for_revealed_links(args)


def fetch_html(args, url):
    if getattr(args, "local_html", False):
        path = Path(url).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Local HTML file not found: {path}")
        return path.read_text(encoding="utf-8", errors="replace")

    if getattr(args, "selenium", False):
        pace_links(args)
        try:
            web.selenium_get_page(args, url)
            reveal_download_links(args)
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


def query_filename(url):
    """Return the filename carried by ?file= (used by the site's dl servers)."""
    query = parse_qs(urlparse(url).query)
    for key in ("file", "filename", "name"):
        values = query.get(key)
        if values:
            name = Path(unquote(values[0])).name
            if name:
                return name
    return ""


def filename_from_url(url):
    filename = query_filename(url) or Path(unquote(urlparse(url).path)).name
    return path_utils.clean_path((filename or "download").encode(), max_name_len=255)


def safe_filename(text, max_len=180):
    text = re.sub(r"[\\/:*?\"<>|]+", "-", text or "download")
    text = re.sub(r"\s+", " ", text).strip(" .") or "download"
    return path_utils.clean_path(text.encode(), max_name_len=max_len)


def link_extension(link):
    name = query_filename(link.url) or unquote(urlparse(link.url).path)
    extension = Path(name).suffix.casefold()
    if extension and extension not in {".html", ".htm", ".php"}:
        return extension.lstrip(".")
    return link.format or "bin"


def output_name_for_link(link, title):
    for name in (
        query_filename(link.url),
        Path(unquote(urlparse(link.url).path)).name,
        link.label,
    ):
        if name and Path(name).suffix.casefold() not in {"", ".html", ".htm", ".php"}:
            return path_utils.clean_path(name.encode(), max_name_len=255)

    label = link.part or link.label or link.format or "download"
    return safe_filename(f"{title} - {label}.{link_extension(link)}")


def safe_path_component(text):
    text = re.sub(r"[\\/:*?\"<>|]+", "-", text or "").strip(" .")
    return text or "unknown"


def download_directory(args, page_url):
    """Return $prefix/$domain/$page/ for the page a download came from."""
    parsed = urlparse(page_url or "")
    domain = parsed.hostname or "local"
    if parsed.hostname:
        path = unquote(parsed.path).rstrip("/")
        if path and Path(path).suffix:
            path = str(Path(path).parent)
        page = Path(path).name or "root"
    else:
        page = Path(unquote(parsed.path)).stem or "root"
    return (
        Path(args.prefix).expanduser()
        / safe_path_component(domain)
        / safe_path_component(page)
    )


def download_file(args, url, output_name=None, page_url=None):
    destination = download_directory(args, page_url or url)
    destination.mkdir(parents=True, exist_ok=True)
    output_path = destination / (output_name or filename_from_url(url))
    pace_links(args)
    try:
        return web.download_url(args, url, str(output_path))
    finally:
        mark_link_finished(args)


def download_selected(args, page_url, page, state, depth=0, output_page_url=None):
    destination_page = output_page_url or page_url
    selected = select_downloads(page)
    if not selected:
        log.warning("No download links found on %s", page_url)
        return False

    if getattr(args, "select_only", False):
        for link in selected:
            print(link.url)
        return True

    for link in selected:
        if state.downloads_blocked:
            return False

        if not is_file_url(link.url):
            max_depth = getattr(args, "max_depth", 2)
            if link.url.startswith(("http://", "https://")):
                if depth >= max_depth:
                    log.warning(
                        "Not following page link at max depth %s: %s",
                        max_depth,
                        link.url,
                    )
                elif getattr(args, "local_html", False):
                    log.info(
                        "Not following remote nested page in --local-html mode: %s",
                        link.url,
                    )
                elif same_site(link.url, page_url):
                    log.info("Following nested download page %s", link.url)
                    process_url(
                        args,
                        link.url,
                        state,
                        depth=depth + 1,
                        match_terms=significant_words(page.title),
                        match_title=page.title,
                        root_page_url=destination_page,
                    )
                else:
                    log.warning(
                        "Skipping external page (not a direct file): %s", link.url
                    )
            else:
                log.warning("Skipping non-file link: %s", link.url)
            continue

        output_name = output_name_for_link(link, page.title)
        log.info("Downloading %s to %s", link.url, output_name)
        try:
            downloaded = download_file(
                args, link.url, output_name=output_name, page_url=destination_page
            )
        except Exception as excinfo:  # noqa: BLE001
            if not is_stop_error(excinfo):
                log.error("Could not download %s: %s", link.url, excinfo)
                continue
            state.downloads_blocked = True
            state.network_stopped = True
            if page_url not in state.remaining_page_urls:
                state.remaining_page_urls.append(page_url)
            log.warning(
                "HTTP 429/403 while downloading %s; stopping downloads", link.url
            )
            return False

        if downloaded:
            print(downloaded)
            state.files_downloaded += 1
        else:
            log.warning("Download failed for %s", link.url)

    return True


def process_url(
    args,
    url,
    state=None,
    depth=0,
    match_terms=None,
    match_title=None,
    root_page_url=None,
):
    """Process one page or file URL; return False when it should stay queued."""
    state = state or RunState()
    root_page_url = root_page_url or url

    if url in state.visited_urls:
        log.debug("Already visited %s; skipping", url)
        return True
    state.visited_urls.add(url)

    if state.network_stopped and not getattr(args, "local_html", False):
        if is_download_page_url(url):
            if url not in state.remaining_page_urls:
                state.remaining_page_urls.append(url)
            log.warning("Queued %s (network stopped after HTTP 429/403)", url)
        else:
            log.warning("Skipping %s: network stopped after HTTP 429/403", url)
        return False

    if is_file_url(url) and not getattr(args, "local_html", False):
        if getattr(args, "select_only", False):
            print(url)
            return True
        if state.downloads_blocked:
            if url not in state.remaining_page_urls:
                state.remaining_page_urls.append(url)
            return False
        try:
            downloaded = download_file(args, url, page_url=root_page_url)
        except Exception as excinfo:
            if not is_stop_error(excinfo):
                raise
            state.downloads_blocked = True
            state.network_stopped = True
            state.remaining_page_urls.append(url)
            log.warning("HTTP 429/403 while downloading %s; stopping downloads", url)
            return False
        if downloaded:
            print(downloaded)
            state.files_downloaded += 1
            return True
        return False

    try:
        html = fetch_html(args, url)
    except Exception as excinfo:
        if not is_stop_error(excinfo):
            raise
        state.downloads_blocked = True
        state.network_stopped = True
        state.remaining_page_urls.append(url)
        log.warning("HTTP 429/403 while fetching %s; stopping network requests", url)
        return False

    if not html:
        log.warning("Could not get a response for %s", url)
        return False

    soup = BeautifulSoup(html, "html.parser")
    base_url = None if getattr(args, "local_html", False) else url
    page = parse_download_page(soup, base_url)

    if not page.links:
        log.warning(
            "No download links found on %s (try a larger --wait; links load via JavaScript)",
            url,
        )
        return False

    log.info("Found %d download link(s) on %r", len(page.links), page.title)

    # A supplemental "DLC available here" link can point at an index of every
    # DLC for the platform. Only follow entries matching the parent game.
    if match_terms and is_listing_page(page):
        matching = [
            link for link in page.links if link_matches_words(link, match_terms)
        ]
        log.info(
            "Nested listing page %s: %d/%d link(s) match %s",
            url,
            len(matching),
            len(page.links),
            ", ".join(sorted(match_terms)),
        )
        if not matching:
            return True
        page = DownloadPage(title=match_title or page.title, links=matching)

    return download_selected(
        args, url, page, state, depth=depth, output_page_url=root_page_url
    )


def print_download_summary(state):
    sys.stdout.flush()
    print(f"Total files downloaded: {state.files_downloaded}", file=sys.stderr)


def main():
    args = parse_args()
    state = RunState()

    try:
        if getattr(args, "drain_backlog", False):
            process_direct_lists(args, state)
        else:
            for url in shell_utils.gen_paths(args):
                process_url(args, url, state)
    finally:
        try:
            if state.remaining_page_urls:
                save_remaining_pages(state.remaining_page_urls)
        finally:
            print_download_summary(state)
            if getattr(args, "selenium", False) and getattr(args, "driver", None):
                web.quit_selenium(args)


if __name__ == "__main__":
    sys.exit(main())
