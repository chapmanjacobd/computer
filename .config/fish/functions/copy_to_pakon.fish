# Defined interactively
function copy_to_pakon
    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files backup:d/_tixati/ ~/d/75_Moviequeue/from_backup/

    stickysync_backup ~/d/00_Metadata/stickysync_rtorrent_audiobooks d/_rtorrent/ /mnt/d/82_Audiobooks/rtorrent/
    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files ~/Downloads/*.torrent backup:.local/data/rtorrent/watch/new/

    set max 50
    for dir in new/ vip_new/ vip_bbc/ nonvip_new/ bbc_nonfree/ lowseeds_small/
        set filled (ssh backup torrent_promote.py .local/data/rtorrent/watch/$dir --reverse -n $max | count)
        set max (math $max-$filled)
        echo $dir $filled $max
    end
    ssh backup 'systemctl --user stop vpn_oracle.service; sleep (minutes 45); systemctl --user restart vpn_oracle.service'
end
