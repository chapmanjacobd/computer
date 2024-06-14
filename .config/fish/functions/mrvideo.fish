function mrvideo
    lb mv ~/d/sync/video/keep/ ~/d/library/video/
    mkdir ~/d/sync/video/keep/

    lb relmv (
        lb watch ~/lb/video.db -E /sync/video/other/ --local -pf -L 2
    ) /mnt/d/sync/video/other/

    lb relmv (
        lb watch ~/lb/video.db -E /sync/video/other/ --local --upper 6 -pf -L 5
    ) /mnt/d/sync/video/other/

    lb fsadd --video ~/lb/video.db /mnt/d/sync/video/other/
end
