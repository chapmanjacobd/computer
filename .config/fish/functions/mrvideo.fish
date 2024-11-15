function mrvideo
    lb mv ~/sync/video/keep/ ~/d/library/video/
    mkdir ~/sync/video/keep/

    lb relmv (
        lb watch ~/lb/video.db -E /sync/video/other/ --local -pf -L 2
    ) ~/sync/video/other/

    lb relmv (
        lb watch ~/lb/video.db -E /sync/video/other/ --local --upper 6 -pf -L 5
    ) ~/sync/video/other/

    lb fsadd --video ~/lb/video.db ~/sync/video/other/
end
