#!/usr/bin/env python3

for torrent in torrent_list:
    for x in torrent.trackers:
        if OLD_TRACKER in x.url:
            newurl = x.url.replace(OLD_TRACKER, NEW_TRACKER)
            print(f"torrent name: {torrent.name}, original url: {x.url}, modified url: {newurl}\n")
            torrent.remove_trackers(urls=x.url)
            torrent.add_trackers(urls=newurl)
