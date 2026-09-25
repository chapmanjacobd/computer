# Defined in /tmp/fish.CLcaOC/gitMoveToNewBranch.fish @ line 2
function git.rebranch.unstaged
    git stash -a && git checkout main && git pull && git stash pop && git checkout -b $argv && wip
end
