# Defined interactively
function screenwidth
    xdotool getdisplaygeometry | cut -f1 -d' '
end
