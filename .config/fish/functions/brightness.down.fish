function brightness.down
    if test pakon = (hostname)
        _screen_brightness_adjust -3
    else
        brightness.set (math (brightness.get)-3)
    end
end
