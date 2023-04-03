function mrvideo
    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --exclude=".*" ~/d/70_Now_Watching/keep/ ~/d/77_Library/

    lb relmv (
        lb watch ~/lb/video.db -E /70_Now_Watching/ --local-only --lower 6 --upper 30 -p f | sort --unique --ignore-case  | head -n 8
    ) /mnt/d/70_Now_Watching/

    lb relmv (
        lb watch ~/lb/video.db -E /70_Now_Watching/ --local-only --upper 6 -p f | sort --unique --ignore-case  | head -n 10
    ) /mnt/d/70_Now_Watching/

    lb fsadd --video ~/lb/video.db /mnt/d/70_Now_Watching/
end
