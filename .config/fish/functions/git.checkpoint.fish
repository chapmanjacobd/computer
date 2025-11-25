# Defined interactively
function git.checkpoint
    git add .
    git stash push --keep-index
end
