# Defined interactively
function copy_to_pakon
    #rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files backup:d/_tixati/ ~/d/dump/video/other/from_backup/
    #ssh backup remove_empty_directories /home/xk/d/_tixati/

    stickysync_backup ~/d/sync/datasets/file-lists/stickysync_rtorrent_audiobooks d/_rtorrent/ /mnt/d/dump/audio/audiobooks/rtorrent/

    for d in ~/d/check/world/seeding/*
        switch $d
            case '*music*'
                stickysync_local ~/d/sync/datasets/file-lists/stickysync_qbittorrent $d ~/d/dump/audio/music/(path basename $d)/
            case '*'
                stickysync_local ~/d/sync/datasets/file-lists/stickysync_qbittorrent $d ~/d/dump/video/(path basename $d)/
        end
    end
    stickysync_local ~/d/sync/datasets/file-lists/stickysync_qbittorrent ~/d/check/world/seeding-porn/ ~/d/dump/porn/video/
end
