# Defined interactively
function displays
    xrandr --query | \grep '\bconnected\b' | cut -f1 -d' '
end
