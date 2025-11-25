# Defined interactively
function brightness.lg.down
    brightness_lg_set (math (brightness_lg_get)-10)
    pkill -f brightness_lg
end
