# Defined via `source`
function mam.search
    optparse $argv

    load.env.mam

    ~/lb/
    python ~/bin/mam_search.py --audiobooks --radio $opts --cookie $MAM_COOKIE ~/lb/sites/mam/mam.db $args
end
