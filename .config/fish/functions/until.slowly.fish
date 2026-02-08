# Defined in /home/xk/.config/fish/functions/until.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function until.slowly
    while not fish -c (string join -- ' ' (string escape -- $argv))
        and sleep 1.4
    end
end
