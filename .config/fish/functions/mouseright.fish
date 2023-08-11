# Defined interactively
function mouseright
    xdotool mousemove --sync 0 0

    xdotool mousemove (math (screenwidth)/4'*3') (math (screenheight)/2)
end
