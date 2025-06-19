# Defined interactively
function resolution --description 'Current resolution'
    xrandr | grep \* | coln 1
end
