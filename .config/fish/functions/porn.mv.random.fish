function porn.mv.random
    lb copy-play-counts ~/lb/tax.db /home/xk/lb/fs/tax.db --source-prefix ~/sync/porn/video/keep/ --target-prefix /mnt/d/

    ~/sync/porn/video/
    folders.empty.delete

    lb mv ~/sync/porn/video/keep/ ~/d/library/porn/video/
    mkdir ~/sync/porn/video/keep/

    lb mv ~/sync/porn/video/mnt/ /mnt/

    lb relmv (
        lb wt ~/lb/fs/tax.db /check/ --portrait -L 40 -u play_count,time_created -p f -E 69_Taxes_Keep -E /keep/ --local
    ) ~/sync/porn/video/

    lb relmv (
        lb wt ~/lb/fs/tax.db /check/ -E 69_Taxes_Keep -E /keep/ --local -FC=+4 -FC=-16 -p bf | shuf | head -n 10
    ) ~/sync/porn/video/

    lb fsadd --video ~/lb/tax.db ~/sync/porn/video/
end
