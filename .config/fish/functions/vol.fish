# Defined interactively
function vol
    pactl set-sink-volume @DEFAULT_SINK@ $argv%
end
