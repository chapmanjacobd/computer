# Defined via `source`
function battery_percent
    if set -q CONTAINER_ID; or set -q container
        return
    end

    if command -vq upower
        upower -i (upower -e | grep 'BAT') | grep percentage | awk '{print $2}'
    else
        acpi -b | awk -F '[:, %]' '{for (i=1; i<=NF; i++) if ($i ~ /^[0-9]+$/) {print $i; exit}}'
    end
end
