# Defined interactively
function resolution.width
    xdotool getdisplaygeometry | cut -f1 -d' '
end
