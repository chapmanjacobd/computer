#!/usr/bin/python3
import argparse
import sys
from bs4 import BeautifulSoup
import re

def extract_wikipedia_articles(html_content):
    """
    Extracts Wikipedia article titles from HTML content.
    The titles are derived from the 'title' attribute of <a> tags
    or by cleaning the URL path if the 'title' attribute is not present.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    article_names = set()

    for a_tag in soup.find_all('a', href=re.compile(r"https://en\.wikipedia\.org/wiki/")):
        # Prioritize the clean 'title' attribute if available
        title = a_tag.get('title')
        if title:
            article_names.add(title)
        else:
            # Fallback to extracting from the href path and cleaning it up
            href = a_tag['href']
            article_path = href.split('/wiki/')[-1].split('#')[0]
            article_name = article_path.replace('_', ' ')
            article_names.add(article_name)

    return sorted(list(article_names))

def main():
    parser = argparse.ArgumentParser(
        description="Extracts Wikipedia article names from an HTML file or standard input."
    )
    # Using argparse.FileType allows the argument to be either a file path or stdin ('-')
    parser.add_argument(
        'html_source',
        nargs='?',  # Makes the argument optional
        type=argparse.FileType('r'),
        default=sys.stdin,
        help="Path to the HTML file to process. If not provided, reads from stdin."
    )
    args = parser.parse_args()

    try:
        html_content = args.html_source.read()
        articles = extract_wikipedia_articles(html_content)
        for article in articles:
            print(article)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Ensure BeautifulSoup is available. If not, the script will fail.
    # The user can install it via: pip install beautifulsoup4
    main()

