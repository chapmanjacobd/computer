# Defined interactively
function tmux.append
    tmux split-window -d fish -c (string join -- ' ' (string escape -- $argv))
    tmux select-layout even-vertical
end
