# Defined via `source`
function qbt.unqueue
    lb database add torrents ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ --delete-files

    ~/.local/data/qbittorrent/queue/
    for s in 127.0.0.1:8080 (servers.ssh.connectable $servers | grep -v pakon | sed "s|\$|:8888|")
        lb torrent info --dl --time-active=-1hour --downloaded=0 --stop --export --delete-files --host $s
    end
    lb database add torrents ~/lb/torrents.db ~/.local/data/qbittorrent/queue/ --force -v
end
