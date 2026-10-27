# Defined interactively
function git.unmerged
    git log --branches --not --remotes --simplify-by-decoration --decorate --oneline
    #git log --branches --not --remotes --oneline --decorate
end
