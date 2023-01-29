# Defined interactively
function gitall
    for g in /home/xk/.git/ /home/xk/j/.git/ /home/xk/mc/.git/ /home/xk/lb/.git/
        git --git-dir=$g $argv
    end
end
