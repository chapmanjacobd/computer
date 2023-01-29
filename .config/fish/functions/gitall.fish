# Defined interactively
function gitall
    for g in /home/xk/ /home/xk/j/ /home/xk/mc/ /home/xk/lb/
        git --git-dir=$g/.git/ --work-tree=$g $argv
    end
end
