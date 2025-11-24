# Defined interactively
function resolution --description 'Current resolution'
    xrandr | grep \* | lines.coln 1
end
