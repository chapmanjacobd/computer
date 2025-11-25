# Defined interactively
function brightness.lg.down
    brightness.lg.set (math (brightness.lg.get)-10)
    pkill -f brightness_lg
end
