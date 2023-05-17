function mrporn
    rsync -a --remove-source-files --backup-dir (date "+%d.%m.%Y") --exclude=".*" ~/d/60_Now_Watching/keep/ ~/d/69_Taxes_Keep/

    lb relmv /mnt/d/60_Now_Watching/69_Taxes/ /mnt/d/69_Taxes/

    lb relmv (
    lb wt --db ~/lb/fs/tax.db --portrait -L 24 -u play_count,time_created -p f -E 60_Now_Watching -E /keep/ --local-only
     ) /mnt/d/60_Now_Watching/
    lb relmv (                                                          lb wt --db ~/lb/fs/tax.db -E /60_Now_Watching/ -E /keep/ --local-only --lower 4 --upper 16 -p bf | shuf | head -n 8
) /mnt/d/60_Now_Watching/

    lb fsadd --video ~/lb/fs/tax.db /mnt/d/60_Now_Watching/
end
