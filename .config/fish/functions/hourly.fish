# Defined interactively
function hourly
    ssh backup torrent_promote.py --out .local/data/qbittorrent/seed/jptvclub/ .local/data/jptv.club/ -n1

    load_env_mam
    ~/.local/bin/mam_upload_credit.sh

    ~/lb/
    set max (python -m xklb.scratch.mam_slots --cookie $MAM_COOKIE)
    if test $max -gt 0
        for dir in new/ vip_new/ vip_bbc/
            set filled (ssh backup torrent_promote.py .local/data/rtorrent/watch/$dir --reverse -n $max | count)
            set max (math $max-$filled)
        end
        for dir in nonvip_new/ bbc_nonfree/ lowseeds_small/
            set filled (ssh backup torrent_promote.py .local/data/rtorrent/watch/$dir -n $max | count)
            set max (math $max-$filled)
        end
    end

end
