function _xcalib.dim_set --argument-names mode
    set -l lockdir $XDG_RUNTIME_DIR
    test -d "$lockdir"; or set lockdir /tmp
    set -l lockfile $lockdir/xcalib.dimming.lock

    # Serialize rapid shortcut presses so each one sees the previous result.
    if command -q flock
        flock -w 10 -E 75 $lockfile fish -c "_xcalib.dim_apply $mode"
        set -l result $status
        if test $result -eq 75
            echo "xcalib: timed out waiting for the dimming lock" >&2
        end
        return $result
    end

    _xcalib.dim_apply $mode
end
