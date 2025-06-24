# Defined via `source`
function mam_search
    filter_opts $argv

    load_env_mam

    ~/lb/
    python ~/bin/mam_search.py --audiobooks --radio $opts --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db $args
end
