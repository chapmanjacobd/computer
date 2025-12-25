# Defined interactively
function torganize
    parallel server.ssh {} qbt_prioritize.py ::: $servers

    if test (count ~/Downloads/\[(seq 0 9)*.torrent) -gt 0
        rsync -auh --remove-sent-files ~/Downloads/\[(seq 0 9)*.torrent backup:.local/data/rtorrent/watch/new/
    end

    lb playlists ~/lb/torrents.db -pa

    lb mv -etorrent ~/Downloads/ ~/.local/data/qbittorrent/queue/
    lb torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ -v --delete-files

    torrents.db.stats
    echo torrents.maintenance
end
