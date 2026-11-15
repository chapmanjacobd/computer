function _brightness.lock --argument-names command
    set -l lockdir $XDG_RUNTIME_DIR
    test -d "$lockdir"; or set lockdir /tmp
    set -l lockfile $lockdir/brightness.lock

    # Serialize concurrent brightness changes. If another change is still
    # running (key repeat), drop this one instead of queueing a backlog.
    if command -q flock
        flock -w 1 -E 75 $lockfile fish -c "$command"
        set -l result $status
        if test $result -eq 75
            echo "brightness: busy; skipping this press" >&2
        end
        return $result
    end

    fish -c "$command"
end
