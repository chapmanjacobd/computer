function mam.update
    ~/lb/
    load.env.mam

    python ~/bin/mam_search.py --audiobooks --books --radio --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db BBC R4
    for q in (cat ~/j/lists/publishers.list)
        python ~/bin/mam_search.py --comics --books --no-title --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db $q
    end
    for q in (cat ~/j/lists/people.narrators.list)
        python ~/bin/mam_search.py --audiobooks --books --radio --no-title --narrator --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db $q
    end
    for q in (cat ~/j/lists/people.authors.list)
        python ~/bin/mam_search.py --audiobooks --books --comics --no-title --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db $q
    end

    for l in (cat ~/j/private/mam_custom_args.txt)
        python ~/bin/mam_search.py --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db (string split ' ' -- $l) ''
    end

    mam.db.dl ~/lb/sites/mam/mam.db
end
