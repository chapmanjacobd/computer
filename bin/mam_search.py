import argparse, json

from library.mediadb import db_media, db_playlists
from library.utils import arggroups, argparse_utils, nums, objects, strings, web
from library.utils.log_utils import log


def parse_args():
    parser = argparse_utils.ArgumentParser()
    parser.add_argument("--base-url", default="https://www.myanonamouse.net")
    parser.add_argument("--title", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--author", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--narrator", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--series", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--description", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--tags", action=argparse.BooleanOptionalAction, default=False)

    parser.add_argument("--categories", "--category", type=int, nargs="+")
    parser.add_argument("--art-books", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--books", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--audiobooks", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--comics", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--cookbooks", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--musicology", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--radio", action=argparse.BooleanOptionalAction, default=False)

    parser.add_argument("--search-in", default="torrents")
    parser.add_argument("--series-id", "--seriesID", type=int)

    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cookie", required=True)
    arggroups.requests(parser)
    arggroups.debug(parser)

    arggroups.database(parser)
    parser.add_argument("search_text", nargs="+")
    args = parser.parse_intermixed_args()
    arggroups.args_post(args, parser, create_db=True)

    web.requests_session(args)  # prepare requests session
    return args


def get_page(args, query_data):
    import pandas as pd

    response = web.session.post(
        f"{args.base_url}/tor/js/loadSearchJSONbasic.php",
        headers={"Content-Type": "application/json"},
        cookies={"mam_id": args.cookie} if args.cookie else None,
        json=query_data,
    )
    response.raise_for_status()
    data = response.json()

    try:
        data_found = data["found"]
        data = data["data"]
    except KeyError:
        if "Nothing returned" in data["error"]:
            log.warning("No results found")
            raise SystemExit(4)
        else:
            raise RuntimeError(data["error"])

    df = pd.DataFrame(data)
    df = df.drop(columns=["cat", "language", "category", "main_cat", "browseflags", "comments", "owner", "leechers"])

    safe_json = objects.fallback(strings.safe_json_loads, {})

    def dict_values_str(d):
        return ", ".join(d.values())

    def dict_values_list(d):
        return list(d.values())

    df["author_info"] = df["author_info"].apply(safe_json).apply(dict_values_str)
    df["narrator_info"] = df["narrator_info"].apply(safe_json).apply(dict_values_str)
    df["series_info"] = df["series_info"].apply(safe_json).apply(dict_values_list)
    df["size_bytes"] = df["size"].apply(nums.human_to_bytes)

    log.info("Fetched %s", len(df))

    return df.to_dict(orient="records"), data_found


def wrangle_request_data(args):
    query_data = {
        "tor": {
            "text": " ".join(args.search_text),
            "browse_lang": [1, 2, 44, 47],
            "srchIn": {
                "title": args.title,
                "author": args.author,
                "narrator": args.narrator,
                "series": args.series,
                "description": args.description,
                "tags": args.tags,
            },
            "searchType": "all",  # fl-VIP, fl, VIP, all
            "searchIn": args.search_in,
            "browseFlagsHideVsShow": 0,
            "cat": args.categories or [],
            "sortType": "dateDesc",
            "startNumber": 0,
            "minSeeders": 0,
            "maxSeeders": 0,
            "minSnatched": 20,
            "maxSnatched": 0,
            "minSize": 0,
            "maxSize": 0,
        },
        "description": "true",
        "thumbnail": "false",
    }

    if args.series_id:
        query_data["tor"]["seriesID"] = args.series_id

    if args.cookbooks:
        query_data["tor"]["cat"].extend([107])
    if args.comics:
        query_data["tor"]["cat"].extend([61])
    if args.audiobooks:
        query_data["tor"]["cat"].extend(
            [
                39,  # Action/Adventure
                40,  # Crime/Thriller
                41,  # Fantasy
                42,  # General Fiction
                45,  # Literary Classics
                46,  # Romance
                47,  # Science Fiction
                48,  # Western
                49,  # Art
                52,  # General Non-Fic
                54,  # History
                55,  # Home/Garden
                59,  # Recreation
                87,  # Mystery
                89,  # Travel/Adventure
                97,  # Crafts
                98,  # Historical Fiction
                99,  # Humor
                100,  # True Crime
                108,  # Urban Fantasy
                111,  # Young Adult
                119,  # Nature
                43,  # Horror
                44,  # Juvenile
                50,  # Biographical
                51,  # Computer/Internet
                53,  # Self-Help
                56,  # Language
                57,  # Math/Science/Tech
                58,  # Pol/Soc/Relig
                83,  # Business
                84,  # Instructional
                85,  # Medical
                88,  # Philosophy
                106,  # Food
            ]
        )
    if args.art_books:
        query_data["tor"]["cat"].extend(
            [
                71,  # Art
                79,  # Magazines/Newspapers
                101,  # Crafts
                118,  # Mixed Collections
                120,  # Nature
            ]
        )
    if args.books:
        query_data["tor"]["cat"].extend(
            [
                60,  # Action/Adventure
                62,  # Crime/Thriller
                63,  # Fantasy
                64,  # General Fiction
                65,  # Horror
                66,  # Juvenile
                67,  # Literary Classics
                68,  # Romance
                69,  # Science Fiction
                70,  # Western
                72,  # Biographical
                73,  # Computer/Internet
                74,  # General Non-Fiction
                75,  # Self-Help
                76,  # History
                77,  # Home/Garden
                78,  # Language
                80,  # Math/Science/Tech
                81,  # Pol/Soc/Relig
                82,  # Recreation
                90,  # Business
                91,  # Instructional
                92,  # Medical
                94,  # Mystery
                95,  # Philosophy
                96,  # Travel/Adventure
                102,  # Historical Fiction
                103,  # Humor
                104,  # True Crime
                109,  # Urban Fantasy
                112,  # Young Adult
                115,  # Illusion/Magic
            ]
        )
    if args.musicology:
        query_data["tor"]["cat"].extend(
            [
                17,  # Music - Complete Editions
                19,  # Guitar/Bass Tabs
                20,  # Individual Sheet
                22,  # Instructional Media - Music
                24,  # Individual Sheet MP3
                26,  # Music Book
                27,  # Music Book MP3
                30,  # Sheet Collection
                31,  # Sheet Collection MP3
                113,  # Lick Library - LTP/Jam With
                114,  # Lick Library - Techniques/QL
                126,  # Instructional Book with Video
            ]
        )
    if args.radio:
        query_data["tor"]["cat"].extend(
            [
                127,  # Comedy
                128,  # Factual/Documentary
                130,  # Drama
                132,  # Reading
            ]
        )
    if len(query_data["tor"]["cat"]) == 0:
        query_data["tor"]["cat"] = [0]
    return query_data


def mam_update_playlist(args, playlist_path):
    query_data = json.loads(playlist_path)

    inserted_items = 0
    current_start = 0
    total_items = None
    while True:
        query_data["tor"]["startNumber"] = current_start
        page_data, len_found = get_page(args, query_data)

        for d in page_data:
            d["playlists_id"] = args.playlists_id
            d["path"] = d.pop("id")
            if not args.force and db_playlists.media_exists(args, d["path"], playlist_path):
                return inserted_items

            d["size"] = d.pop("size_bytes")
            d |= db_media.consolidate(d) or {}
            args.db["media"].insert(objects.dict_filter_bool(d), pk=["playlists_id", "path"], alter=True, replace=True)
            inserted_items += 1

        if total_items is None:  # first request
            total_items = len_found
        current_start += len(page_data)
        if current_start >= total_items:
            break

        web.sleep(args, secs=2)

    return inserted_items


def mam_search():
    args = parse_args()
    db_playlists.create(args)
    db_media.create(args)

    query_data = wrangle_request_data(args)
    playlist_path = json.dumps(query_data, sort_keys=True)
    args.playlists_id = db_playlists.add(args, playlist_path, {}, extractor_key="MAMSearch")

    new_media = mam_update_playlist(args, playlist_path)
    log.info("Saved %s new media", new_media)


if __name__ == "__main__":
    mam_search()
