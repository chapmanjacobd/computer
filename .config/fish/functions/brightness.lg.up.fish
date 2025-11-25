# Defined interactively
function brightness.lg.up
    brightness.lg.set (math (brightness.lg.get)+5)
    pkill -f brightness_lg
end
