#!/usr/bin/python3
import re
import sys
from bs4 import BeautifulSoup
from collections import defaultdict

def process_html(html_snippet):
    soup = BeautifulSoup(html_snippet, 'html.parser')
    rows = soup.find_all('tr')

    data = []
    for i in range(0, len(rows) - 1, 2):
        title_row, content_row = rows[i], rows[i + 1]

        title_link = title_row.find('a', class_='text-bright')
        size_span = content_row.find('span', class_='badge-extra text-blue')
        peers_link_span = content_row.find('span', class_='badge-extra text-green')

        if title_link and size_span and peers_link_span:
            title = title_link.text.strip()

            peers_link_a = peers_link_span.find_parent('a')
            print(peers_link_a)
            if peers_link_a and peers_link_a['href'].endswith('/peers') and int(peers_link_span.text.strip()) > 0:
                size_value = convert_size_to_bytes(size_span.text.strip())
                data.append({'title': title, 'link': peers_link_a['href'], 'size': size_value})

    print(len(data), data)

    grouped_data = defaultdict(list)
    for item in data:
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', item['title'])
        if date_match:
            date = date_match.group(1)
            grouped_data[date].append(item)
        else:
            print(f"Warning: Date not found in title: {item['title']}")

    result = []
    for date, items in grouped_data.items():
        if items:
            min_size_item = min(items, key=lambda x: x['size'])
            result.append(min_size_item)

    for item in result:
        print(item['link'])

def convert_size_to_bytes(size_str):
    size_str = size_str.replace('\xa0', ' ')
    units = {'MiB': 1024 * 1024, 'GiB': 1024 * 1024 * 1024}
    try:
        value, unit = size_str.split()
        return float(value) * units[unit]
    except (ValueError, KeyError):
        return float('inf')

html_snippet = sys.stdin.read()
process_html(html_snippet)
