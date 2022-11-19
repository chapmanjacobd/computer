# Defined interactively
function tmuxcleanup
    while test (count (tmux list-windows -t phone | grep -i fish | grep -iv active)) -gt 0
        tmux kill-window -t phone:(tmux list-windows -t phone | grep -i fish | grep -iv active | head -1 | cut -d: -f1)
    end
end
