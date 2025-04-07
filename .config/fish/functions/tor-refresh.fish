# Defined interactively
function tor-refresh
    tempdir
    for s in pakon backup r730xd len hk
        lb links --cookies-from-browser firefox --path-include /download/torrent/ --download (ssh -t $s qbt_torrents_refresh.py)
        ssh -t $s lb torrents --tagged library-refresh --untag library-refresh --start
    end
    trash-put (pwd)
end
