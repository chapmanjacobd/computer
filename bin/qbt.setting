#!/usr/bin/python3
from library.mediafiles import torrents_start
from library.utils import arggroups, argparse_utils, objects, printing, processes, strings


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

existing = {k: v for k, v in preferences.items() if args.key == k}
if len(existing) == 0:
    existing = {k: v for k, v in preferences.items() if args.key in k}
if len(existing) == 0:
    processes.exit_error(f'No matches for {args.key} in {preferences.keys()}')

if args.value and len(existing.keys()) > 1:
    selected_keys = processes.fzf_select(existing.keys(), multi=False)
    existing = {k: v for k, v in existing.items() if k in selected_keys}
    args.key = selected_keys[0]

printing.extended_view(existing)
print()

if args.key not in existing:
    processes.exit_error(f'{args.key} not in {existing.keys()}')
if args.value == '':
    processes.exit_error('Value not set')

new_pref = {args.key: args.value}
printing.extended_view(new_pref)

preferences = qbt_client.app_set_preferences(new_pref)
print()

preferences = qbt_client.app_preferences()
existing = objects.dict_filter_similar_key(preferences, args.key)
printing.extended_view(existing)
