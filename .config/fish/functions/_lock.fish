function _lock --argument-names name command
    set -l lockdir $XDG_RUNTIME_DIR
    test -d "$lockdir"; or set lockdir /tmp
    set -l lockfile $lockdir/$name.lock

    # Serialize key-repeat work. Calls arriving while a command is in flight
    # are dropped; the command itself sleeps after each change to throttle.
    if command -q flock
        flock -n -E 75 $lockfile fish -c "$command"
        set -l result $status
        test $result -eq 75; and return 0
        return $result
    end

    fish -c "$command"
end
