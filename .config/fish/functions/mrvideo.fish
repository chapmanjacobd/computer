function mrvideo
    lb relmv (
        lb watch ~/lb/video.db -E /70_Now_Watching/ --local-only --lower 6 --upper 30 -p bf | shuf  | head -n 2
    ) /mnt/d/70_Now_Watching/

    lb relmv (
        lb watch ~/lb/video.db -E /70_Now_Watching/ --local-only --upper 6 -p bf | shuf | head -n 5
    ) /mnt/d/70_Now_Watching/

    lb fsadd --video ~/lb/video.db /mnt/d/70_Now_Watching/
end
