# Defined in /home/xk/.config/fish/functions/tmux.append.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function tmux.append.window
    if test -t 0
        tmux new-window -d -- fish -c (string join -- ' ' (string escape -- $argv))
    else
        while read -l cmd
            tmux new-window -d -- $cmd
        end
    end
end
