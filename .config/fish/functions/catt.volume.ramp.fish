# Defined via `source`
function catt.volume.ramp --argument target_volume
    if not string match -qr '^[1-9][0-9]?$|^100$' $target_volume
        echo "Error: Target volume must be an integer between 1 and 100."
        return 1
    end

    set current_volume (catt info | grep 'volume_level:' | awk '{print $2}')
    set current_volume (math -s 0 "$current_volume * 100")

    if test $current_volume -lt $target_volume
        while test $current_volume -lt $target_volume
            set current_volume (math $current_volume + 1)
            catt volume $current_volume
            sleep 2
        end
    else
        while test $current_volume -gt $target_volume
            set current_volume (math $current_volume - 1)
            catt volume $current_volume
            sleep 2
        end
    end
end
