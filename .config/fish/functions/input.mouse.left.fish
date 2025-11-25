# Defined interactively
function input.mouse.left
    xdotool mousemove --sync (resolution.width) 0

    xdotool mousemove (math (resolution.width)/4) (math (resolution.height)/2)
end
