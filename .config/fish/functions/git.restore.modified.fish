# Defined interactively
function git.restore.modified
    git diff
    git restore (git-status-filter M M)
end
