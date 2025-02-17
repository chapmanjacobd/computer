# Defined via `source`
function mam_search
    filter_opts $argv

    load_env_mam

    ~/lb/
    python -m library.scratch.mam_search --audiobooks --radio $opts --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db $args
end
