function _xcalib.dim_set --argument-names mode
    set -l lockdir $XDG_RUNTIME_DIR
    test -d "$lockdir"; or set lockdir /tmp
    set -l lockfile $lockdir/xcalib.dimming.lock

    # Serialize dim steps. Presses arriving while a step is in flight are
    # dropped; the delay after each step throttles key repeat.
    if command -q flock
        flock -n -E 75 $lockfile fish -c "_xcalib.dim_apply $mode"
        set -l result $status
        test $result -eq 75; and return 0
        return $result
    end

    _xcalib.dim_apply $mode
end
