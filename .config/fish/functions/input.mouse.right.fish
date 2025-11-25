# Defined interactively
function input.mouse.right
    xdotool mousemove --sync 0 0

    xdotool mousemove (math (resolution.width)/4'*3') (math (resolution.height)/2)
end
