function dbackups
    wol b8:97:5a:09:b0:be
    while not ssh backup grep -qs '/mnt/d ' /proc/mounts
        sleep 5
        notify-send 'Turn on the backup server'
    end

    rsync -ah --info=progress2 --no-inc-recursive --exclude video --exclude audio ~/sync/ backup:~/d/sync/
    # rsync -ah --info=progress2 --no-inc-recursive /mnt/d/archive/ backup:/mnt/d/archive/

    ~/
    rsync -ah --files-from=(lb media ~/lb/fs/audio.db -w 'play_count > 0' -pf | sed 's|/mnt/d/||' | psub) /mnt/d/ backup:/mnt/d/

    # ssh backup sudo systemctl poweroff
end
