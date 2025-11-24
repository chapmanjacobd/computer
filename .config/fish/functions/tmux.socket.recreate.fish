# Defined via `source`
function tmux.socket.recreate
    pkill -SIGUSR1 tmux
end
