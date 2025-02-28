# Defined interactively
function torganize
    parallel sshpc {} qbt_prioritize.py ::: pakon backup r730xd len hk
    # ~/bin/qbt_file_sizes.py -v 127.0.0.1:8080 backup:8888 r730xd:8888 hk:8888 len:8888

    rsync -auh --remove-sent-files ~/Downloads/\[(seq 0 9)*.torrent backup:.local/data/rtorrent/watch/new/

    lb mv ~/Downloads/*.torrent ~/.local/data/qbittorrent/queue/
    lb torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ -v --delete-files

    # ~/bin/qbt_torrents_exfoliate.py

    lb computer-add ~/lb/computers.local.db pakon backup r730xd len -v
    lb computer-add ~/lb/computers.remote.db hk -v

    qbt_computers_remaining.py ~/lb/computers.local.db
    qbt_computers_remaining.py ~/lb/computers.remote.db

    tor-refresh
end
