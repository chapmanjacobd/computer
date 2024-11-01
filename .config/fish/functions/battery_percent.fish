# Defined interactively
function battery_percent
    if set -q CONTAINER_ID; or set -q container
        return
    end

    upower -i (upower -e | grep 'BAT') | grep percentage | awk '{print $2}'
end
