# Defined interactively
function brightness.up
    if test pakon = (hostname)
        _screen_brightness_adjust +1
    else
        brightness.set (math (brightness.get)+1)
    end
end
