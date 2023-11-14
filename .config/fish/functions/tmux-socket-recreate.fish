# Defined interactively
function tmux-socket-recreate
    kill -SIGUSR1 (pgrep tmux)
end
