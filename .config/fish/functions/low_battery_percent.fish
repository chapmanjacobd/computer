# Defined interactively
function low_battery_percent
    set battery_percentage (battery_percent)

    if test (echo $battery_percentage | sed 's/%//') -lt 60
        echo $battery_percentage
    else
        echo ""
    end

end
