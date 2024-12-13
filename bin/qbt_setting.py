#!/usr/bin/python3
from library.mediafiles import torrents_start
from library.utils import arggroups, argparse_utils, printing, strings, objects

def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    parser.add_argument('key')
    parser.add_argument('value', type=strings.load_string)
    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
preferences = qbt_client.app_preferences()

existing = objects.dict_filter_similar_key(preferences, args.key)

printing.extended_view(existing)
print()

new_pref = {args.key: args.value}
printing.extended_view(new_pref)

preferences = qbt_client.app_set_preferences(new_pref)
print()

preferences = qbt_client.app_preferences()
existing = objects.dict_filter_similar_key(preferences, args.key)
printing.extended_view(existing)
