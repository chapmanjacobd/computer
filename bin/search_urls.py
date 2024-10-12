#!/usr/bin/python3
import argparse
import re
import urllib.parse


def main(args=None):
    parser = argparse.ArgumentParser(description='Expand a search URL with multiple queries.')
    parser.add_argument(
        '--search-urls', '-s', action='append', required=True, help='List of search URLs with a placeholder "%s".'
    )
    parser.add_argument('queries', nargs='+', help='List of queries to replace the placeholder with.')
    args = parser.parse_intermixed_args(args)
    # print(args)

    for query in args.queries:
        for search_url in args.search_urls:
            words = re.findall(r'\w+', query)
            # print("words", words)
            words = [word for word in words if word]
            encoded_query = urllib.parse.quote(' '.join(words))

            if "%s" not in search_url:
                raise SystemExit(f"Error: No '%s' in provided search_url '{search_url}'")

            expanded_url = search_url.replace("%s", encoded_query)
            print(expanded_url)

'''
import shlex
import pytest

@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        ('-s t%s 1', "t1"),
        ('-s t%s \n1\n', "t1"),
        ('-s t%s "\'1\'"', "t1"),
        ('-s t%s \'"1"\'', "t1"),
        ('-s t%s "1 [20]"', "t1 20"),
        ('-s t%s "1 (20)"', "t1 20"),
        ('-s t%s 1 2 3', "t1\nt2\nt3"),
    ],
)
def test_main(capsys, argv, expected):
    main(shlex.split(argv))
    assert capsys.readouterr().out.strip() == expected.replace(' ', '%20')
'''

if __name__ == "__main__":
    main()
