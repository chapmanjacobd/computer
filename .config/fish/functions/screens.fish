# Defined interactively
function screens
    xrandr --query | \grep '\bconnected\b' | cut -f1 -d' '
end
