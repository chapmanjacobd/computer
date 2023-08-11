# Defined interactively
function mouseleft
    xdotool mousemove --sync (screenwidth) 0
    
    xdotool mousemove (math (screenwidth)/4) (math (screenheight)/2)
end
