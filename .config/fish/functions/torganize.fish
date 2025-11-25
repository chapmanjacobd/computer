# Defined interactively
function torganize
    parallel server.ssh {} qbt_prioritize.py ::: $servers

    if test (count ~/Downloads/\[(seq 0 9)*.torrent) -gt 0
        rsync -auh --remove-sent-files ~/Downloads/\[(seq 0 9)*.torrent backup:.local/data/rtorrent/watch/new/
    end

    lb playlists ~/lb/torrents.db -pa

    lb mv -etorrent ~/Downloads/ ~/.local/data/qbittorrent/queue/
    lb torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ -v --delete-files

    lb computer-add ~/lb/computers.local.db (connectable-ssh $servers_local) -v
    for pc in (connectable-ssh $servers_remote)
        lb computer-add ~/lb/computers.remote.db $pc -v
    end

    qbt_computers_remaining.py ~/lb/computers.local.db
    #qbt_computers_remaining.py ~/lb/computers.remote.db

    torrents.db.stats
    echo torrents.maintenance
end
