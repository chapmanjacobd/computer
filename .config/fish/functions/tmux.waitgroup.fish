# Defined interactively
function tmux.waitgroup
    set -l session_id (random)
    set -l signals

    for cmd in $argv
        set -l sig "sig_$session_id"_(random)
        set -a signals $sig
        # The window runs the command, then signals it is done
        tmux new-window "$cmd; tmux wait-for -S $sig"
    end

    for sig in $signals
        tmux wait-for $sig
    end
end
