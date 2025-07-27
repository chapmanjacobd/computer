#!/usr/bin/python3
import webbrowser
import argparse
import urllib.parse

def generate_ebay_url(term_groups):
    base_url = "https://www.ebay.com/sch/i.html"

    if not term_groups:
        print("Error: No search term groups provided for URL generation.")
        return None

    formatted_parts = []
    for group in term_groups:
        formatted_group = "(" + ",".join([item.replace(" ", "+") for item in group]) + ")"
        formatted_parts.append(formatted_group)
    combined_nkw = "".join(formatted_parts)

    encoded_nkw = urllib.parse.quote(combined_nkw)
    full_url = f"{base_url}?_nkw={encoded_nkw}&_sacat=0"

    return full_url

def main():
    parser = argparse.ArgumentParser(
        description="Converts lists of search terms into an eBay search URL and opens it. "
                    "Terms are grouped by a separator."
    )
    parser.add_argument(
        "search_terms",
        nargs="+",
        help='All search terms, separated into groups by separator. '
             'Example: 2TB 3TB; U.3 "SATA M.2"; SSD'
    )
    args = parser.parse_args()

    sep = ";"

    term_groups = []
    current_group = []
    for term in args.search_terms:
        if term == sep or term.endswith(sep):
            if current_group:
                term_groups.append(current_group)
            current_group = []  # start a new group
        else:
            current_group.append(term.rstrip(sep))
    if current_group: # last group
        term_groups.append(current_group)

    url = generate_ebay_url(term_groups)
    if url:
        print(url)
        webbrowser.open(url)

if __name__ == "__main__":
    main()
