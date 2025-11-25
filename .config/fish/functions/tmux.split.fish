# Defined interactively
function tmux.split --argument n
    repeatn $n tmux split-window -v
    tmux select-layout even-vertical
end
