function mam_update
    ~/lb/
    load_env_mam

    python -m xklb.scratch.mam_search --audiobooks --books --radio --cookie $MAM_COOKIE ~/d/library/datasets/links/mam/mam.db BBC R4
    for q in (cat ~/j/lists/publishers.list)
        python -m xklb.scratch.mam_search --comics --books --no-title --cookie $MAM_COOKIE ~/d/library/datasets/links/mam/mam.db $q
    end
    for q in (cat ~/j/lists/people.narrators.list)
        python -m xklb.scratch.mam_search --audiobooks --books --radio --no-title --narrator --cookie $MAM_COOKIE ~/d/library/datasets/links/mam/mam.db $q
    end

    for l in (cat ~/j/private/mam_custom_args.txt)
        python -m xklb.scratch.mam_search --cookie $MAM_COOKIE ~/d/library/datasets/links/mam/mam.db (string split ' ' -- $l) ''
    end

    for db in ~/d/library/datasets/links/mam/mam.db
        sqlite --no-headers --raw-lines "$db" "select id from media where added > datetime('now', '-7 days') and vip=1 and seeders>0" | sed "s|^|curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid=|" | parallel -S backup -j4 ".local/data/rtorrent/watch/vip_new/; eval {}"
        sqlite --no-headers --raw-lines "$db" "select id from media where added > datetime('now', '-7 days') and vip=0 and seeders>0" | sed "s|^|curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid=|" | parallel -S backup -j4 ".local/data/rtorrent/watch/nonvip_new/; eval {}"
    end

end
