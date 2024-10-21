#!/usr/bin/python3
import argparse
import re

from bs4 import BeautifulSoup
from xklb.utils import arggroups, argparse_utils


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.debug(parser)

    parser.add_argument("input_paths", nargs="*", type=argparse.FileType("r"), help="Paths to process")
    args = parser.parse_args()
    arggroups.args_post(args, parser)

    if not args.input_paths:
        args.input_paths = [argparse.FileType("r")("-")]

    return args


def html_to_markdown(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    def convert_links(tag):
        return f"[{tag.get_text()}]({tag["href"]})"

    def convert_code(tag):
        return f"`{tag.get_text()}`"

    def convert_fenced_code(tag):
        language = tag.get("class", [""])[0].replace("language-", "")
        code_content = tag.get_text()
        return f"""
```{language}
{code_content}
```
"""

    markdown_content = soup.get_text()

    for link in soup.find_all("a"):
        markdown_content = markdown_content.replace(link.get_text(), convert_links(link))

    for code in soup.find_all("code"):
        if code.parent.name == "pre":
            markdown_content = markdown_content.replace(code.get_text(), convert_fenced_code(code))
        else:
            markdown_content = markdown_content.replace(code.get_text(), convert_code(code))

    # Clean up any remaining HTML tags
    markdown_content = re.sub(r"<[^>]+>", "", markdown_content)

    return markdown_content




def html2simplemd():
    args = parse_args()

    for path in args.input_paths:
        html_content = path.read()

        markdown_content = html_to_markdown(html_content)
        print(markdown_content)


if __name__ == "__main__":
    html2simplemd()
