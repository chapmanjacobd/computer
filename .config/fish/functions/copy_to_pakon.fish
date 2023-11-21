# Defined interactively
function copy_to_pakon
    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files backup:d/_tixati/ ~/d/75_Moviequeue/from_backup/
    ssh backup remove_empty_directories /home/xk/d/_tixati/

    stickysync_backup ~/d/00_Metadata/stickysync_rtorrent_audiobooks d/_rtorrent/ /mnt/d/82_Audiobooks/rtorrent/
    stickysync_backup ~/d/00_Metadata/stickysync_qbittorrent d/_qbittorrent/ /mnt/d/75_Moviequeue/From_Backup/

    # ssh backup 'pkill tixati; systemctl --user stop vpn_oracle.service; sleep (minutes 45); systemctl --user restart vpn_oracle.service; sleep 20; run tixati'
end
