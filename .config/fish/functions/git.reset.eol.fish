# Defined interactively
function git.reset.eol
    git rm --cached -- $argv
    git restore --source=HEAD --staged --worktree -- $argv
end
