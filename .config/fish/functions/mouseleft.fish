# Defined interactively
function mouseleft
    xdotool mousemove --sync (resolution.width) 0

    xdotool mousemove (math (resolution.width)/4) (math (screenheight)/2)
end
