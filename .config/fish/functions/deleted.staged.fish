# Defined interactively
function deleted.staged --wraps='git status'
    git-status-filter D " " $argv
end
