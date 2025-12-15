# Defined interactively
function changedtype.staged --wraps='git status'
    git-status-filter T " " $argv
end
