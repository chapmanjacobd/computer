# Defined interactively
function git-eol-reset
    git rm --cached -- $argv
    git restore --source=HEAD --staged --worktree -- $argv
end
