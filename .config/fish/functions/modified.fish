# Defined interactively
function modified --wraps='git status'
    git-status-filter " " M $argv
end
