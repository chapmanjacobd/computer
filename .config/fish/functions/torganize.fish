# Defined interactively
function torganize
    parallel sshpc {} qbt_prioritize.py ::: pakon backup r730xd len hk

    rsync -auh --remove-sent-files ~/Downloads/\[(seq 0 9)*.torrent backup:.local/data/rtorrent/watch/new/

    lb mv ~/Downloads/*.torrent ~/.local/data/qbittorrent/queue/
    lb torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ -v --delete-files

    # ~/bin/qbt_torrents_exfoliate.py

    lb computer-add ~/lb/computers.local.db pakon backup r730xd len -v
    lb computer-add ~/lb/computers.remote.db hk -v

    tor-refresh

    # torstart

    #torrent_promote.py --trackers -n9999 -o ~/.local/data/qbittorrent/ ~/Downloads/

    #rsync -auh --remove-sent-files ~/Downloads/*.torrent backup:.local/data/qbittorrent/seed_pause/others/
end
