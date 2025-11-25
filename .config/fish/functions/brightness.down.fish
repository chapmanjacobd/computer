# Defined interactively
function brightness.down
    if test pakon = (hostname)
        brightness.lg.down
    else
        brightness_set (math "$(brightness_get)-(3*$(brightness_step))")
    end
end
