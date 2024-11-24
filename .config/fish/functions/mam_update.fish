function mam_update
    ~/lb/
    load_env_mam

    python -m xklb.scratch.mam_search --audiobooks --books --radio --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db BBC R4
    for q in (cat ~/j/lists/publishers.list)
        python -m xklb.scratch.mam_search --comics --books --no-title --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db $q
    end
    for q in (cat ~/j/lists/people.narrators.list)
        python -m xklb.scratch.mam_search --audiobooks --books --radio --no-title --narrator --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db $q
    end
    for q in (cat ~/j/lists/people.authors.list)
        python -m xklb.scratch.mam_search --audiobooks --books --comics --no-title --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db $q
    end

    for l in (cat ~/j/private/mam_custom_args.txt)
        python -m xklb.scratch.mam_search --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db (string split ' ' -- $l) ''
    end

    for db in ~/lb/sites/mam/mam.db
        sqlite --no-headers --raw-lines "$db" "select id from media where unixepoch(added) > $(timestamp 1 week ago 0 -u) and vip=1 and seeders>0 and my_snatched=0" | parallel -S backup -j1 ".local/data/rtorrent/watch/vip_new/; curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid={}; sleep 2"
        sqlite --no-headers --raw-lines "$db" "select id from media where unixepoch(added) > $(timestamp 1 week ago 0 -u) and vip=0 and seeders>0 and my_snatched=0" | parallel -S backup -j1 ".local/data/rtorrent/watch/nonvip_new/; curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid={}; sleep 2"
    end

end
