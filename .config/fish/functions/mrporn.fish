function mrporn
    ~/d/60_Now_Watching/
    remove_empty_directories
    lb relmv /mnt/d/60_Now_Watching/69_Taxes/ /mnt/d/69_Taxes/
    lb relmv ~/d/60_Now_Watching/keep/ ~/d/69_Taxes_Keep/

    lb relmv (
        lb wt ~/lb/fs/tax.db --portrait -L 24 -u play_count,time_created -p f -E 69_Taxes_Keep -E /keep/ --local
    ) /mnt/d/60_Now_Watching/

    lb relmv (
        lb wt ~/lb/fs/tax.db -E 69_Taxes_Keep -E /keep/ --local --lower 4 --upper 16 -p bf | shuf | head -n 8
    ) /mnt/d/60_Now_Watching/

    lb fsadd --video ~/lb/fs/tax.db /mnt/d/60_Now_Watching/
end
