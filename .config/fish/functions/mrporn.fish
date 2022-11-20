function mrporn
    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --exclude=".*" ~/d/60_Now_Watching/keep/ ~/d/69_Taxes_Keep/

    rsync -a --remove-source-files --files-from=(
        lb wt ~/lb/fs/tax.db --portrait -L 24 -u play_count,time_created -p f -E 60_Now_Watching -s 69 --moved /mnt/d/ /mnt/d/60_Now_Watching/ | psub
    ) /mnt/d/ /mnt/d/60_Now_Watching/

    rsync -a --remove-source-files --files-from=(
        lb wt ~/lb/fs/tax.db -L 48 -u 'play_count,duration desc' -p f -E 60_Now_Watching -s 69 --moved /mnt/d/ /mnt/d/60_Now_Watching/ | psub
    ) /mnt/d/ /mnt/d/60_Now_Watching/

    lb fsadd --video ~/lb/fs/tax.db /mnt/d/60_Now_Watching/
end
