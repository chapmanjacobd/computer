# Defined via `source`
function qbt-unqueue
    lb torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ --delete-files

    ~/.local/data/qbittorrent/queue/
    for s in r730xd:8888 backup:8888 127.0.0.1:8080
        lb torrents --dl --time-active=-1hour --downloaded=0 --stop --export --delete-files --host $s
    end
    lb torrents-add ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ --force -v
end
