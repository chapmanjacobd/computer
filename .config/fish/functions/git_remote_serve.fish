# Defined interactively
function git_remote_serve
    git remote -v
    git remote remove origin
    git config receive.denyCurrentBranch updateInstead
end
