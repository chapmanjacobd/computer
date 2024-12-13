# Defined via `source`
function mam_search
    filter_opts $argv

    load_env_mam
    set db ~/lb/sites/mam/(string replace -a ' ' _ $args).db

    ~/lb/
    python -m library.scratch.mam_search --audiobooks --books --comics --radio $opts --cookie $MAM_COOKIE "$db" $args

    mam_db_dl "$db"
end
