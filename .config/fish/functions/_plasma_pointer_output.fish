function _plasma_pointer_output
    # kdotool reports the cursor in logical (compositor) coordinates.
    set -l location
    if command -q kdotool
        set location (kdotool getmouselocation --shell 2>/dev/null)
    else if set -q DISPLAY; and command -q xdotool
        set location (xdotool getmouselocation --shell 2>/dev/null)
    end
    test -n "$location"; or return 1

    set -l x (string match -r '^X=[0-9]+' -- $location | string replace 'X=' '')
    set -l y (string match -r '^Y=[0-9]+' -- $location | string replace 'Y=' '')
    test -n "$x" -a -n "$y"; or return 1

    kscreenctl list-outputs --json 2>/dev/null |
        jq -r --argjson x $x --argjson y $y '
            .[]
            | select(.enabled and .position != null and .mode != null)
            | select(
                $x >= .position.x
                and $x < .position.x + (.mode.resolution.width / .scale)
                and $y >= .position.y
                and $y < .position.y + (.mode.resolution.height / .scale)
            )
            | .name
        ' |
        head -n 1
end
