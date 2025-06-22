function watts
    set -l apcupsd_was_inactive false

    if not systemctl is-active --quiet apcupsd
        set apcupsd_was_inactive true
        sudo systemctl start apcupsd
        if test $status -ne 0
            return 1
        end

        sleep 5
    end

    set -l PERCENT (apcaccess -pLOADPCT | sed 's/Percent//')
    set -l UPSMAXWATTS (apcaccess -pNOMPOWER | sed 's/Watts//')

    if $apcupsd_was_inactive
        sudo systemctl stop apcupsd
    end

    if test -n "$PERCENT" -a -n "$UPSMAXWATTS"
        echo (math "$PERCENT * $UPSMAXWATTS / 100")
    else
        return 2
    end
end
