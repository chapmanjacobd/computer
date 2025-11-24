function porn.mv.random
    lb copy-play-counts ~/lb/tax.db /home/xk/lb/fs/tax.db --source-prefix ~/sync/porn/video/keep/ --target-prefix /mnt/d/

    ~/sync/porn/video/
    remove_empty_directories

    lb mv ~/sync/porn/video/keep/ ~/d/library/porn/video/
    mkdir ~/sync/porn/video/keep/

    lb mv ~/sync/porn/video/mnt/ /mnt/

    lb relmv (
        lb wt ~/lb/fs/tax.db /check/ --portrait -L 24 -u play_count,time_created -p f -E 69_Taxes_Keep -E /keep/ --local
    ) ~/sync/porn/video/

    lb relmv (
        lb wt ~/lb/fs/tax.db /check/ -E 69_Taxes_Keep -E /keep/ --local -FC=+4 -FC=-16 -p bf | shuf | head -n 8
    ) ~/sync/porn/video/

    lb fsadd --video ~/lb/tax.db ~/sync/porn/video/
end
