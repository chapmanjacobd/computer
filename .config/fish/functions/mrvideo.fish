function mrvideo
    lb relmv (
        lb watch ~/lb/video.db -E /70_Now_Watching/ --local -pf -L 2
    ) /mnt/d/70_Now_Watching/

    lb relmv (
        lb watch ~/lb/video.db -E /70_Now_Watching/ --local --upper 6 -pf -L 5
    ) /mnt/d/70_Now_Watching/

    lb fsadd --video ~/lb/video.db /mnt/d/70_Now_Watching/
end
