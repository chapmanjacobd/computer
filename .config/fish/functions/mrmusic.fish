function mrmusic
    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --files-from=(lt --db ~/lb/audio.db -s /mnt/d/80_Now_Listening/ -p f --moved /mnt/d/80_Now_Listening/ /mnt/d/ | psub) /mnt/d/80_Now_Listening/ /mnt/d/

    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --files-from=(
        lt --db ~/lb/audio.db --local-media-only -w 'play_count=0' -u random -L 400 -p f --moved /mnt/d/ /mnt/d/80_Now_Listening/ | psub
    ) /mnt/d/ /mnt/d/80_Now_Listening/

    lb fsadd --audio ~/lb/audio.db /mnt/d/80_Now_Listening/
end
