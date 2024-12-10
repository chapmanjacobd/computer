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

    mam_db_dl ~/lb/sites/mam/mam.db
end

# mam_search individual and then
# lb merge-dbs using id as bk
