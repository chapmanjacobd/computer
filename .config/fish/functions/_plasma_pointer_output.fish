function _plasma_pointer_output
    # kdotool asks KWin for the cursor position in logical coordinates.
    if command -q kdotool
        set -l location (kdotool getmouselocation --shell 2>/dev/null)
        set -l x (string match -r '^X=[0-9]+' -- $location | string replace 'X=' '')
        set -l y (string match -r '^Y=[0-9]+' -- $location | string replace 'Y=' '')
        if test -n "$x" -a -n "$y"
            set -l output (
                kscreen-doctor -o 2>&1 |
                    sed -E 's/\x1B\[[0-9;]*m//g' |
                    awk -v x=$x -v y=$y '
                        /^Output: / { name = $3; enabled = 0; next }
                        /^\tenabled$/ { enabled = 1; next }
                        /^\tGeometry:/ {
                            if (!enabled) next
                            split($2, position, ",")
                            split($3, size, "x")
                            if (x >= position[1] && x < position[1] + size[1] && y >= position[2] && y < position[2] + size[2]) {
                                print name
                                exit
                            }
                        }
                    '
            )
            test -n "$output"; and echo $output
            return
        end
    end

    # Fallback for sessions without kdotool: XWayland exposes per-monitor geometry.
    set -q DISPLAY; or return 1
    command -q xdotool; or return 1
    command -q xrandr; or return 1

    set -l location (xdotool getmouselocation --shell 2>/dev/null)
    set -l x (string match -r '^X=[0-9]+' -- $location | string replace 'X=' '')
    set -l y (string match -r '^Y=[0-9]+' -- $location | string replace 'Y=' '')
    if test -z "$x" -o -z "$y"
        return 1
    end

    set -l output (
        xrandr --listmonitors 2>/dev/null | awk -v x=$x -v y=$y '
            $1 ~ /^[0-9]+:$/ {
                split($3, geometry, /[\/x+]/)
                offsetx = geometry[5]
                offsety = geometry[6]
                if (x >= offsetx && x < offsetx + geometry[1] && y >= offsety && y < offsety + geometry[3]) {
                    print $4
                    exit
                }
            }
        '
    )
    test -n "$output"; and echo $output
end
