# Defined interactively
function gitresetindex
    trash .git/index
    git reset
    git update-index --skip-worktree -- (git status --porcelain | grep '^ M' | cut -f3 -d' ')
end
