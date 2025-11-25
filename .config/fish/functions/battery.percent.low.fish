# Defined interactively
function battery.percent.low
    set battery_percentage (battery.percent)

    if test -n "$battery_percentage"
        if test (echo $battery_percentage | sed 's/%//') -lt 60
            echo $battery_percentage
        end
    end

end
