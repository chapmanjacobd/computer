# Defined interactively
function tmuxsplit --argument n
    repeatn $n tmux split-window -v
    tmux select-layout even-vertical
end
