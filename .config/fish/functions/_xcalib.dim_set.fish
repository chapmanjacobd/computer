function _xcalib.dim_set --argument-names mode
    set -l lockdir $XDG_RUNTIME_DIR
    test -d "$lockdir"; or set lockdir /tmp
    set -l lockfile $lockdir/xcalib.dimming.lock

    # Serialize rapid shortcut presses so each one sees the previous result.
    if command -q flock
        if not flock -w 10 $lockfile fish -c "_xcalib.dim_apply $mode"
            echo "xcalib: timed out waiting for the dimming lock" >&2
            return 1
        end
    else
        _xcalib.dim_apply $mode
    end
end
