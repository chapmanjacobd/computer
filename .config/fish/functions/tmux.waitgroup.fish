# Defined via `source`
function tmux.waitgroup
    set -l session_id (random)
    set -l signals

    args.or.stdin $argv | while read -l cmd
        set -l sig "sig_$session_id"_(random)
        set -a signals $sig
        # The window runs the command, then signals it is done
        tmux new-window "$cmd; tmux wait-for -S $sig"
    end

    for sig in $signals
        tmux wait-for $sig
    end
end
