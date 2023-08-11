# Defined interactively
function screenheight
    xdotool getdisplaygeometry | cut -f2 -d' '
end
