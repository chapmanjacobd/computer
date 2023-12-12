# Defined interactively
function copy_to_pakon
    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files backup:d/_tixati/ ~/d/75_Moviequeue/from_backup/
    ssh backup remove_empty_directories /home/xk/d/_tixati/

    stickysync_backup ~/d/00_Metadata/stickysync_rtorrent_audiobooks d/_rtorrent/ /mnt/d/82_Audiobooks/rtorrent/

    for d in ~/d/24_Seeding/*
        stickysync_local ~/d/00_Metadata/stickysync_qbittorrent $d ~/d/75_Moviequeue/From_Backup/
    end
end
