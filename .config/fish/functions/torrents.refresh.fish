# Defined interactively
function torrents.refresh
    set call_dir (pwd)
    tempdir
    for s in (servers.ssh.connectable $servers)
        set urls (ssh -T $s qbt_torrents_refresh.py)
        if test -n "$urls"
            lb links --cookies-from-browser firefox --path-include /download/torrent/ --download $urls
            ssh -T $s lb torrents --tagged library-refresh --untag library-refresh --start
        end
    end
    trash (pwd)
    cd $call_dir
end
