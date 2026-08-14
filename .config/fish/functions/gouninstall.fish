# Defined in /home/xk/.config/fish/functions/cargouninstall.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function gouninstall
    for arg in $argv
        file.lines.filter ~/.github/go_installed $arg
        rm (which $arg)
    end
end
