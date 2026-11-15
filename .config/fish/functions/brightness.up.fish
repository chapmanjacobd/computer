# Defined interactively
function brightness.up
    if test pakon = (hostname)
        _screen_brightness_adjust +5
    else
        brightness.set (math (brightness.get)+(brightness.step))
    end
end
