# Defined interactively
function input.mouse.right
    if command -q dotool
        printf 'mouseto 0 0\nmouseto 0.75 0.5\n' | _dotool
        return
    end

    set -l size (_screen.size)
    set -l width (string split ' ' -- $size)[1]
    set -l height (string split ' ' -- $size)[2]
    xdotool mousemove --sync 0 0
    xdotool mousemove (math "$width/4*3") (math "$height/2")
end
