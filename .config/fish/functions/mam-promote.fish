function mam-promote -a max
    load_env_mam

    ~/lb/
    if test $max -gt 0
        for dir in new/
            set filled (ssh backup torrent_promote.py .local/data/rtorrent/watch/$dir -n $max | count)
            set max (math $max-$filled)
        end
        for dir in vip_new/
            set filled (ssh backup torrent_promote.py .local/data/rtorrent/watch/$dir --reverse -n $max | count)
            set max (math $max-$filled)
        end
        for dir in nonvip_new/
            set filled (ssh backup torrent_promote.py .local/data/rtorrent/watch/$dir -n $max | count)
            set max (math $max-$filled)
        end
    end
end
