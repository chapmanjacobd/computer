# Defined interactively
function battery_percent
    upower -i (upower -e | grep 'BAT') | grep percentage | awk '{print $2}'
end
