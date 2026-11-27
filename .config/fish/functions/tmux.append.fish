# Defined interactively
function tmux.append --wraps='tmux'
    tmux split-window -d fish -c (string join -- ' ' (string escape -- $argv))
    tmux select-layout even-vertical
end
