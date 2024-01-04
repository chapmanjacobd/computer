# Defined via `source`
function mam_search
    filter_opts $argv

    load_env_mam
    set db ~/d/library/datasets/links/mam/(string replace -a ' ' _ $args).db

    ~/lb/
    python -m xklb.scratch.mam_search --audiobooks --books --comics --radio $opts --cookie $MAM_COOKIE "$db" $args

    sqlite --no-headers --raw-lines "$db" 'select id from media where vip=1 and seeders>0' | sed "s|^|curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid=|" | parallel -S backup -j4 '.local/data/rtorrent/watch/vip_new/; eval {}'
    sqlite --no-headers --raw-lines "$db" 'select id from media where vip=0 and seeders>0' | sed "s|^|curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid=|" | parallel -S backup -j4 '.local/data/rtorrent/watch/nonvip_new/; eval {}'
end
