# Defined interactively
function brightness.up
    if test pakon = (hostname)
        _screen_brightness_adjust +2
    else
        brightness.set (math (brightness.get)+2)
    end
end
