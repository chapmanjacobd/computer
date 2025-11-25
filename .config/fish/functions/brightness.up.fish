# Defined interactively
function brightness.up
    if test pakon = (hostname)
        brightness.lg.up
    else
        brightness_set (math (brightness_get)+(brightness.step))
    end
end
