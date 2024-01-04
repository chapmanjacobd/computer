function mrmusic
    lb relmv /mnt/d/sync/audio/weekly/ /mnt/d/

    lb relmv (
        lt --db ~/lb/audio.db --local-media-only -w 'play_count=0' -u random -L 600 -p f
    ) /mnt/d/sync/audio/weekly/

    lb relmv (
        lb listen ~/lb/audio.db -E /sync/audio/music/ --local --lower 4 --upper 16 -p bf | shuf | head -n 8
    ) /mnt/d/sync/audio/weekly/
end
