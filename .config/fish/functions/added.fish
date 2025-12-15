# Defined interactively
function added --wraps='git status'
    git-status-filter A " " $argv
end
