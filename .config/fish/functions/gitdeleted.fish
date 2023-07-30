# Defined interactively
function gitdeleted --wraps='git diff'
    git diff --name-status $argv | grep ^D | cut -f2
end
