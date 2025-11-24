# Defined via `source`
function with.lock
    set -l lockfile "$XDG_RUNTIME_DIR/$argv[1].lock"
    set -l command $argv[2..-1]

    if flock -n "$lockfile" $command
        rm "$lockfile"
    else
        echo "Couldn't acquire lock $lockfile. Process is already running." >&2
        return 1
    end
end
