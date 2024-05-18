function mrmusic
    rclone move /mnt/d/sync/audio/weekly/ /mnt/d/check/audio/

    lb relmv (
        lb media ~/lb/audio.db --local -w 'play_count=0' -u random --fetch-siblings if-audiobook -L 600 -p f
    ) /mnt/d/sync/audio/weekly/

    lb relmv (
        lb media ~/lb/audio.db --local -E /sync/audio/ -w 'play_count=0' -FC=+4 -FC=-16 -p bf | shuf | head -n 8
    ) /mnt/d/sync/audio/weekly/
end
