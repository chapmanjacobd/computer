# Defined interactively
function gitstash-checkpoint
    git add .
    git stash push --keep-index
end
