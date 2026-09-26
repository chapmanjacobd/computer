# Defined interactively
function torganize
    parallel server.ssh {} qbt.prioritize ::: $servers

    set rtorrent_files
    for torrent in (fd --no-ignore --max-depth=1 -e torrent --changed-before 5mins ~/Downloads/)
        if string match -rq '\[[0-9].*\.torrent$' -- $torrent; and strings $torrent | rg -q 't.myan'
            set --append rtorrent_files $torrent
        end
    end
    if test (count $rtorrent_files) -gt 0
        lb mv $rtorrent_files ~/.local/data/rtorrent/watch/new/
    end

    lb playlists ~/lb/torrents.db -pa

    set files (fd --no-ignore --max-depth 1 '.torrent$' --changed-before '5min' ~/Downloads/)
    if test (count $files) -gt 0
        lb mv $files ~/.local/data/qbittorrent/queue/
    end
    lb torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ -v --delete-files

    torrents.db.stats
    echo torrents.maintenance
end
