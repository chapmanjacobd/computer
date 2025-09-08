function mrmusic
    lb copy-play-counts ~/lb/audio.db /home/xk/lb/fs/audio.db --source-prefix ~/sync/audio/weekly/ --target-prefix /mnt/d/

    lb mv ~/sync/audio/weekly/ /mnt/d/check/audio/

    lb relmv (
        lb media ~/lb/fs/audio.db --local -w 'play_count=0' -u random --fetch-siblings if-audiobook -L 1600 -p f
    ) ~/sync/audio/weekly/

    lb relmv (
        lb media ~/lb/fs/audio.db --local -E /sync/audio/ -w 'play_count=0' -FC=+4 -FC=-16 -p bf --folders | shuf | head -n 30
    ) ~/sync/audio/weekly/

    lb christen --run ~/sync/audio/
    files_casefold.py ~/sync/audio/ --run
end
