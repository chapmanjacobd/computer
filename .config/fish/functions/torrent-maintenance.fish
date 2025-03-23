# Defined interactively
function torrent-maintenance
    ~/bin/qbt_hashes.py -v 127.0.0.1:8080 backup:8888 r730xd:8888 hk:8888 len:8888
    ~/bin/qbt_file_sizes.py -v 127.0.0.1:8080 backup:8888 r730xd:8888 hk:8888 len:8888

    for s in 127.0.0.1:8080 backup:8888 r730xd:8888 hk:8888 len:8888
        qbt_torrents_exfoliate.py --host $s
        qbt_torrents_trumped.py --host $s
    end

    for s in pakon backup r730xd len hk
        # remove previously tagged items
        ssh $s library torrents --tagged library-trumped --stop --delete-incomplete --move processing(datestamp) --delete-rows
    end

end
