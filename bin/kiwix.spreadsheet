#!/usr/bin/env python3

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

import xmltodict


def parse_opds_to_csv(input_file: str, output_file: str = None):
    """
    Parse OPDS atom feed and convert to CSV.

    Args:
        input_file: Path to the entries.atom file
        output_file: Path to output CSV file (defaults to entries.csv)
    """
    # Read and parse the XML
    with open(input_file, 'r', encoding='utf-8') as f:
        catalog = xmltodict.parse(f.read())

    if 'feed' not in catalog:
        raise ValueError("Invalid OPDS feed: missing 'feed' element")

    feed = catalog['feed']

    if not int(feed.get('totalResults', 0)):
        print("Warning: Catalog has no entries", file=sys.stderr)
        return

    entries = feed.get('entry', [])

    # Ensure entries is a list (single entry may be returned as dict)
    if isinstance(entries, dict):
        entries = [entries]

    # Determine output file
    if output_file is None:
        output_file = str(Path(input_file).with_suffix('.csv'))

    # Define CSV headers
    headers = [
        'uuid',
        'name',
        'title',
        'description',
        'author',
        'publisher',
        'languages',
        'tags',
        'flavour',
        'category',
        'size_bytes',
        'size_human',
        'url',
        'torrent_url',
        'illustration_url',
        'version',
        'updated',
    ]

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for entry in entries:
            if not entry.get('name'):
                print(f"Warning: Skipping entry without name: {entry.get('id', 'unknown')}",
                      file=sys.stderr)
                continue

            # Parse links
            links = {}
            for link in entry.get('link', []):
                if isinstance(link, dict) and '@type' in link:
                    links[link['@type']] = link

            # Extract version from updated field
            updated = entry.get('updated', '')
            try:
                version = datetime.fromisoformat(
                    re.sub(r'[A-Z]$', '', updated)
                ).strftime('%Y-%m-%d')
            except (ValueError, AttributeError):
                version = updated

            # Get author and publisher
            author = entry.get('author', {})
            if isinstance(author, dict):
                author = author.get('name', '')

            publisher = entry.get('publisher', {})
            if isinstance(publisher, dict):
                publisher = publisher.get('name', '')

            # Get ZIM URL
            zim_link = links.get('application/x-zim', {})
            zim_url = zim_link.get('@href', '')
            zim_url = re.sub(r'.meta4$', '', zim_url)

            # Get size
            size_bytes = int(zim_link.get('@length', 0))

            # Format size for human readability
            size_human = format_size(size_bytes)

            # Get illustration URL
            illustration = links.get('image/png;width=48;height=48;scale=1', {})
            illustration_url = illustration.get('@href', '')

            # Parse tags for category
            tags = entry.get('tags', '')
            tags_list = [t.strip() for t in tags.split(';') if t.strip()]

            category = ''
            for tag in tags_list:
                if tag.startswith('_category:'):
                    category = tag.split(':', 1)[1]
                    break

            # Parse languages
            languages = entry.get('language', 'eng')

            row = {
                'uuid': entry.get('id', ''),
                'name': entry.get('name', ''),
                'title': entry.get('title', ''),
                'description': entry.get('summary', ''),
                'author': author,
                'publisher': publisher,
                'languages': languages,
                'tags': tags,
                'flavour': entry.get('flavour', ''),
                'category': category,
                'size_bytes': size_bytes,
                'size_human': size_human,
                'url': zim_url,
                'illustration_url': illustration_url,
                'version': version,
                'updated': updated,
            }

            writer.writerow(row)

    print(f"Successfully converted {len(entries)} entries to {output_file}")


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    if size_bytes < 0:
        return "Unknown"

    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.2f} PiB"


def main():
    parser = argparse.ArgumentParser(
        description='Convert OPDS entries.atom file to CSV format'
    )
    parser.add_argument(
        'input_file',
        help='Path to the entries.atom file'
    )
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Path to output CSV file (default: entries.csv in same directory)',
        default=None
    )

    args = parser.parse_args()

    try:
        parse_opds_to_csv(args.input_file, args.output_file)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
