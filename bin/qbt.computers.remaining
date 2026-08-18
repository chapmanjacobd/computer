#!/usr/bin/python3
import os
import sqlite3

import qbittorrentapi
from library.utils import arggroups, argparse_utils, strings
from library.utils.log_utils import log


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    arggroups.database(parser)
    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

with args.db.conn:
    try:
        args.db.conn.execute("ALTER TABLE media ADD COLUMN allocated INTEGER")
    except sqlite3.OperationalError as e:
        if "duplicate column name: allocated" in str(e):
            pass
        else:
            raise

disks = list(
    args.db.query(
        """
        SELECT
            computers.path host
            , disks.path mountpoint
            , disks.free
        FROM media AS disks
        JOIN playlists AS computers ON computers.id = disks.playlists_id
        """
    )
)

disks_by_host = {}
for d in disks:
    disks_by_host.setdefault(d['host'], []).append(d)

for host, host_disks in disks_by_host.items():
    port = 8080 if host == 'pakon' else 8888
    qbt_client = qbittorrentapi.Client(
        host=host,
        port=port,
        username=args.username,
        password=args.password,
    )

    try:
        torrents = qbt_client.torrents_info()
    except (qbittorrentapi.APIConnectionError, ConnectionRefusedError):
        log.error("ConnectionError: skipping %s %s", host, port)
        continue

    host_disks = sorted(host_disks, key=len, reverse=True)
    torrents_by_disk = {}
    for t in torrents:
        for d in host_disks:
            if (t.content_path or t.save_path).startswith(d['mountpoint'] + os.sep):
                torrents_by_disk.setdefault(d['mountpoint'], []).append(t)
                break

    for disk in host_disks:
        mountpoint = disk['mountpoint']
        if mountpoint not in torrents_by_disk:
            continue

        disk_torrents = torrents_by_disk[mountpoint]
        remaining = sum(t.amount_left for t in disk_torrents)

        if remaining > disk['free']:
            log.warning(
                '%s %s allocation exceeds free space by %s',
                host,
                mountpoint,
                strings.file_size(abs(disk['free'] - remaining)),
            )

        log.info(
            '%s %s has %s torrents (%s allocated)', host, mountpoint, len(disk_torrents), strings.file_size(remaining)
        )

        with args.db.conn:
            args.db.conn.execute(
                """
                UPDATE media
                SET allocated = :allocated
                WHERE 1=1
                AND playlists_id = (SELECT id from playlists WHERE path = :host)
                AND path = :mountpoint
            """,
                {
                    'host': host,
                    'mountpoint': mountpoint,
                    'allocated': remaining,
                },
            )
