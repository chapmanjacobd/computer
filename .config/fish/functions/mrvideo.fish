function mrvideo
    lb copy-play-counts ~/lb/video.db /home/xk/lb/fs/video.db --source-prefix ~/sync/video/keep/ --target-prefix /mnt/d/

    lb mv ~/sync/video/keep/ ~/d/library/video/
    mkdir ~/sync/video/keep/

    lb relmv (
        lb watch ~/lb/fs/video.db -E /sync/video/other/ --local -pf -L 2
    ) ~/sync/video/other/

    lb relmv (
        lb watch ~/lb/fs/video.db -E /sync/video/other/ --local --upper 6 -pf -L 5
    ) ~/sync/video/other/

    lb fsadd --video ~/lb/fs/video.db ~/sync/video/other/

    lb mv -eMKA -eMP3 -eOPUS ~/sync/video/ ~/sync/audio/
end
