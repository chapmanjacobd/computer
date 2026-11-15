# Defined interactively
function brightness.down
    if test pakon = (hostname)
        _screen_brightness_adjust -10
    else
        brightness.set (math "$(brightness.get)-(3*$(brightness.step))")
    end
end
