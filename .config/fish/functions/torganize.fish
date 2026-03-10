# Defined interactively
function torganize
    parallel server.ssh {} qbt_prioritize.py ::: $servers

    if test (count ~/Downloads/\[(seq 0 9)*.torrent) -gt 0
        lb mv (fd --max-depth=1 '\[[0-9].*\.torrent' --changed-before 5mins ~/Downloads/) /net/backup/.local/data/rtorrent/watch/new/
    end

    lb playlists ~/lb/torrents.db -pa

    set files (fd --max-depth 1 '.torrent$' --changed-before '5min' ~/Downloads/)
    if test (count $files) -gt 0
        lb mv $files ~/.local/data/qbittorrent/queue/
    end
    lb torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ -v --delete-files

    torrents.db.stats
    echo torrents.maintenance
end
