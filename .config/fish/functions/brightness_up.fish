# Defined interactively
function brightness_up
    if test pakon = (hostname)
        brightness_lg_up
    else
        brightness_set (math (brightness_get)+1)
    end
end
