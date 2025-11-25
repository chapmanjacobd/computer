# Defined interactively
function brightness.lg.up
    brightness_lg_set (math (brightness_lg_get)+5)
    pkill -f brightness_lg
end
