# Defined interactively
function torganize
    rsync -auh --remove-sent-files ~/Downloads/\[(seq 0 9)*.torrent backup:.local/data/rtorrent/watch/new/

    lb mv ~/Downloads/*.torrent ~/.local/data/qbittorrent/queue/
    lb-dev torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/

    #torrent_promote.py --trackers -n9999 -o ~/.local/data/qbittorrent/ ~/Downloads/

    #rsync -auh --remove-sent-files ~/Downloads/*.torrent backup:.local/data/qbittorrent/seed_pause/others/
end
