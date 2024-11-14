# Defined interactively
function brightness_down
    if test pakon = (hostname)
        brightness_lg_down
    else
        brightness_set (math (brightness_get)-3)
    end
end
