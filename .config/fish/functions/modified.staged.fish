# Defined interactively
function modified.staged --wraps='git status'
    git-status-filter M " " $argv
end
