function torrent-maintenance
    set hosts (connectable-ssh backup r730xd len hk | sed "s|\$|:8888|")

    ~/bin/qbt_hashes.py -v 127.0.0.1:8080 $hosts
    ~/bin/qbt_file_sizes.py -v 127.0.0.1:8080 $hosts

    tor-refresh

    # tag items
    for s in 127.0.0.1:8080 $hosts
        qbt_torrents_exfoliate.py --host $s
        qbt_torrents_trumped.py --host $s
    end
    # remove tagged items
    for s in pakon backup r730xd len hk
        ssh -T $s library torrents --tagged library-trumped --stop --delete-incomplete --move processing/(datestamp) --delete-rows -pa
    end

    allpc lb torrents --ul --no-any-exists --no-checking --no-errored --move processing --delete-rows -v -pa

    allqb lb torrents --dl --downloaded=+0 --time-active=+1days --force-start -pa >/dev/null
    allqb lb torrents --ul --no-force-start -pa >/dev/null

    lb-dev torrents --dl --dl-speed=-3M --no-queued --no-stopped --force-start -pa >/dev/null
end
