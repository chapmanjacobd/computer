# Defined interactively
function smartctl.lbas
    for dev in (smartctl.ls Total_LBAs_Written | tail -n +2 | cut -f1)
        echo $dev

        set ss (sudo blockdev --getss $dev)
        for att in Total_LBAs_Written Total_LBAs_Read
            set val (sudo smartctl -a $dev | grep $att | awk '{print $10}')
            printf "%s\t%s\n" $att (math "$val*$ss")
        end | numfmt --to=iec --invalid ignore --field=2
    end
end
