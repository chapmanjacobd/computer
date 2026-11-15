function _brightness.lg_lock --argument-names command
    set -l lockdir $XDG_RUNTIME_DIR
    test -d "$lockdir"; or set lockdir /tmp
    set -l lockfile $lockdir/brightness.lg.lock

    # Serialize concurrent DDC/CI access from rapid presses and timers.
    if command -q flock
        flock -w 30 -E 75 $lockfile fish -c "$command"
        set -l result $status
        if test $result -eq 75
            echo "brightness.lg: timed out waiting for the brightness lock" >&2
        end
        return $result
    end

    fish -c "$command"
end
