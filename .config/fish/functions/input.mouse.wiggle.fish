# Defined interactively
function input.mouse.wiggle
    if command -q dotool
        printf 'mousemove %s %s\n' (random -20 20) (random -20 20) | _dotool
        return
    end

    xdotool mousemove (random 40 80) (random 40 80)
end
