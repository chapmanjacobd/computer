# Defined interactively
function deleted --wraps='git status'
    git-status-filter " " D $argv
end
