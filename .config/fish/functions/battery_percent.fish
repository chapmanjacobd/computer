# Defined via `source`
function battery_percent
    if set -q CONTAINER_ID; or set -q container
        return
    end

    if command -vq upower
        upower -i (upower -e | grep 'BAT') | grep percentage | awk '{print $2}'
    else
        acpi -b | grep -oP '\d+%' | sed 's/%//g' | head -1
    end
end
