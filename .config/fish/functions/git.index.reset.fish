# Defined interactively
function git.index.reset
    trash .git/index
    git reset
    git update-index --skip-worktree -- (git status --porcelain | grep '^ M' | cut -f3 -d' ')
end
