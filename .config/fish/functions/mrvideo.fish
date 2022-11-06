function mrvideo
    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --exclude=".*" ~/d/70_Now_Watching/keep/ ~/d/77_Library/

    rsync -a --remove-source-files --files-from=(
        wt ~/lb/video.db -L 24 -p wf --moved /mnt/d/ /mnt/d/70_Now_Watching/ | psub
    ) /mnt/d/ /mnt/d/70_Now_Watching/

    lb fsadd --video ~/lb/video.db /mnt/d/70_Now_Watching/
end
