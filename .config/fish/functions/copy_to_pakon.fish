# Defined interactively
function copy_to_pakon
    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files backup:d/_tixati/ ~/d/75_Moviequeue/from_backup/

    stickysync_backup ~/d/00_Metadata/stickysync_rtorrent_audiobooks d/_rtorrent/ /mnt/d/82_Audiobooks/rtorrent/
    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files ~/Downloads/*.torrent backup:.local/data/rtorrent/watch/new/
    ssh backup torrent_promote.py .local/data/rtorrent/watch/vip_bbc/ --reverse -n 50
    ssh backup 'systemctl --user stop vpn_oracle.service; sleep (minutes 45); systemctl --user restart vpn_oracle.service'

    # ~/d/75_Moviequeue/from_backup/
    # fd '[a-zA-Z]{2,5}-?[0-9]{3}' -x mv {} /mnt/d/69_Taxes/onejav/
    # fd '^[a-zA-Z]{3,}-[0-9]{3,5}' -x mv {} /mnt/d/69_Taxes/onejav/
    # remove_empty_directories .
end
