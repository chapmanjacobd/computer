# Defined interactively
function tor-refresh
    set call_dir (pwd)
    tempdir
    for s in (connectable-ssh pakon backup r730xd len hk)
        set urls (ssh -T $s qbt_torrents_refresh.py)
        if test -n "$urls"
            lb links --cookies-from-browser firefox --path-include /download/torrent/ --download $urls
            ssh -T $s lb torrents --tagged library-refresh --untag library-refresh --start
        end
    end
    trash (pwd)
    cd $call_dir
end
