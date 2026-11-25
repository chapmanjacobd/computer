# Defined interactively
function input.mouse.left
    if command -q dotool
        printf 'mouseto 1 0\nmouseto 0.25 0.5\n' | _dotool
        return
    end

    set -l size (_screen.size)
    set -l width (string split ' ' -- $size)[1]
    set -l height (string split ' ' -- $size)[2]
    xdotool mousemove --sync $width 0
    xdotool mousemove (math "$width/4") (math "$height/2")
end
