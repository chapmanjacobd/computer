# Defined in /home/xk/.config/fish/functions/git.ignore.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function stignore --description 'Add path(s) to .gitignore'
    for arg in $argv
        set rel (realpath --relative-to=. $arg)
        echo /$rel >> .stignore
    end
end
