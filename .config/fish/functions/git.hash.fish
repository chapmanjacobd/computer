# Defined interactively
function git.hash
    git rev-parse HEAD
    #git write-tree
    #git rev-parse (git rev-parse HEAD)^{tree}
end
