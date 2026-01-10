# Defined in /home/xk/.config/fish/functions/tmux.append.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function tmux.append.window
    tmux new-window -d fish -c (string join -- ' ' (string escape -- $argv))
end
