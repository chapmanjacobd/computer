function mrmusic
    lb mv ~/sync/audio/weekly/ /mnt/d/check/audio/

    lb relmv (
        lb media ~/lb/audio.db --local -w 'play_count=0' -u random --fetch-siblings if-audiobook -L 1100 -p f
    ) ~/sync/audio/weekly/

    lb relmv (
        lb media ~/lb/audio.db --local -E /sync/audio/ -w 'play_count=0' -FC=+4 -FC=-16 -p bf --folders | shuf | head -n 25
    ) ~/sync/audio/weekly/
end
