function _xcalib.dim_set --argument-names mode
    set -l lockdir $XDG_RUNTIME_DIR
    test -d "$lockdir"; or set lockdir /tmp
    set -l lockfile $lockdir/xcalib.dimming.lock

    # Serialize rapid shortcut presses. If a press is already running, drop
    # this one rather than queueing a backlog of steps.
    if command -q flock
        flock -w 1 -E 75 $lockfile fish -c "_xcalib.dim_apply $mode"
        set -l result $status
        if test $result -eq 75
            echo "xcalib: busy; skipping this press" >&2
        end
        return $result
    end

    _xcalib.dim_apply $mode
end
