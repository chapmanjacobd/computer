function mrmusic
    lb relmv /mnt/d/80_Now_Listening/ /mnt/d/

    lb relmv (
        lt --db ~/lb/audio.db --local-media-only -w 'play_count=0' -u random -L 600 -p f
    ) /mnt/d/80_Now_Listening/

    lb relmv (
        lb listen ~/lb/audio.db -E /80_Now_Listening/ --local --lower 4 --upper 16 -p bf | shuf | head -n 8
    ) /mnt/d/80_Now_Listening/
end
