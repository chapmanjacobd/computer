#!/usr/bin/python3
import argparse
import sys
import urllib.parse

import requests
from bs4 import BeautifulSoup


class ArgsOrStdin(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not values or values == ['-']:
            lines = sys.stdin.readlines()
        else:
            lines = values
        setattr(namespace, self.dest, lines)


parser = argparse.ArgumentParser()
parser.add_argument('paths', nargs='*', action=ArgsOrStdin)
args = parser.parse_args()


def fake_title(url):
    p = urllib.parse.urlparse(url)
    title = f'{p.netloc} {p.path} {p.params} {p.query}: {p.fragment}'

    if title.startswith('www.'):
        title = title[4:]

    title = title.replace('/', ' ')
    title = title.replace('?', ' ')
    title = title.replace('#', ': ')

    return title.strip()


for url in args.paths:
    url = url.strip()

    try:
        res = requests.get(url.strip())
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.title.text.strip() if soup.title else url
    except requests.exceptions.RequestException as e:
        title = fake_title(url)

    text = f'[{title}]({url})'
    if len(args.paths) > 1:
        print(f'- {text}')
    else:
        print(text)
