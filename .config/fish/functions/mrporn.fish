function mrporn
    ~/d/sync/porn/video/
    remove_empty_directories
    lb relmv /mnt/d/sync/porn/video/dump/porn/video/ /mnt/d/dump/porn/video/
    lb relmv ~/d/sync/porn/video/keep/ ~/d/library/porn/video/

    lb relmv (
        lb wt ~/lb/tax.db --portrait -L 24 -u play_count,time_created -p f -E 69_Taxes_Keep -E /keep/ --local
    ) /mnt/d/sync/porn/video/

    lb relmv (
        lb wt ~/lb/tax.db -E 69_Taxes_Keep -E /keep/ --local --lower 4 --upper 16 -p bf | shuf | head -n 8
    ) /mnt/d/sync/porn/video/

    lb fsadd --video ~/lb/tax.db /mnt/d/sync/porn/video/
end
