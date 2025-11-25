# Defined interactively
function resolution.height
    xdotool getdisplaygeometry | cut -f2 -d' '
end
