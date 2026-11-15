function _brightness.lock --argument-names command
    set -l lockdir $XDG_RUNTIME_DIR
    test -d "$lockdir"; or set lockdir /tmp
    set -l lockfile $lockdir/brightness.lock

    # Serialize brightness changes. Presses arriving while a change is in
    # flight are dropped; the delay after each change throttles key repeat.
    if command -q flock
        flock -n -E 75 $lockfile fish -c "$command"
        set -l result $status
        test $result -eq 75; and return 0
        return $result
    end

    fish -c "$command"
end
