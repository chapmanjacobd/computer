# Defined interactively
function hourly
    load_env_mam
    ~/bin/mam_upload_credit.sh

    ~/lb/
    set max (python -m library.scratch.mam_slots --max 4 --cookie $MAM_COOKIE)
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

    torganize
end
