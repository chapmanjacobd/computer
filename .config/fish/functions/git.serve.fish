# Defined interactively
function git.serve
    git remote -v
    git remote remove origin
    git config receive.denyCurrentBranch updateInstead
end
