# Defined interactively
function tmux-append
    tmux new-split -d fish -c (string join -- ' ' (string escape -- $argv))
end
