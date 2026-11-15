function _screen.set_mode --argument-names output mode
    # kscreenctl matches resolution and refresh tightly, so resolve the closest
    # available refresh rate instead (e.g. 3440x1440@160 -> @159.96).
    set -l resolution (string replace -r '@.*' '' -- $mode)
    set -l target (string replace -r '.*@' '' -- $mode)

    set -l id (kscreenctl $output list-modes |
        awk -F'[:@]' -v resolution=$resolution -v target=$target '
            $2 == resolution {
                refresh = $3 + 0
                difference = refresh - target
                if (difference < 0) difference = -difference
                if (best == "" || difference < best_difference) {
                    best = $1
                    best_difference = difference
                }
            }
            END { if (best != "") print best }
        ')

    if test -z "$id"
        echo "screen: mode $mode not found on $output" >&2
        return 1
    end

    kscreenctl $output set-mode $id
end
