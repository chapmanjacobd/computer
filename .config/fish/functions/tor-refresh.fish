# Defined interactively
function tor-refresh
    tempdir
    for s in pakon backup r730xd len hk
        set urls (ssh -t $s qbt_torrents_refresh.py)
        if test -n "$urls"
            lb links --cookies-from-browser firefox --path-include /download/torrent/ --download $urls
            ssh -t $s lb torrents --tagged library-refresh --untag library-refresh --start
        end
    end
    trash-put (pwd)
end
