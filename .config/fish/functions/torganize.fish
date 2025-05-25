# Defined interactively
function torganize
    parallel sshpc {} qbt_prioritize.py ::: pakon backup r730xd len hk

    rsync -auh --remove-sent-files ~/Downloads/\[(seq 0 9)*.torrent backup:.local/data/rtorrent/watch/new/

    lb playlists ~/lb/torrents.db -pa

    lb mv ~/Downloads/*.torrent ~/.local/data/qbittorrent/queue/
    lb torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ -v --delete-files

    lb computer-add ~/lb/computers.local.db pakon backup r730xd len -v
    lb computer-add ~/lb/computers.remote.db hk -v

    qbt_computers_remaining.py ~/lb/computers.local.db
    qbt_computers_remaining.py ~/lb/computers.remote.db

    lb playlists ~/lb/torrents.db -pa
    duckdb ~/lb/torrents.db "select tracker, count(*), format_bytes(sum(size)::BIGINT) size from playlists WHERE time_deleted=0 group by 1 order by sum(size)"
    echo torrent-maintenance
end
