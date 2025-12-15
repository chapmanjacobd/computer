# Defined interactively
function changedtype --wraps='git status'
    git-status-filter " " T $argv
end
