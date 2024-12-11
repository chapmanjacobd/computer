# Defined interactively
function hourly
    ssh backup torrent_promote.py --out .local/data/qbittorrent/seed/jptvclub/ .local/data/jptv.club/ -n1

    load_env_mam
    ~/bin/mam_upload_credit.sh

    ~/lb/
    # set max (math -s0 (python -m xklb.scratch.mam_slots --cookie $MAM_COOKIE)/4)
    set max (python -m xklb.scratch.mam_slots --max 4 --cookie $MAM_COOKIE)
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
