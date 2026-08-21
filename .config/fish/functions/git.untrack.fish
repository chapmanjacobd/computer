# Defined interactively
function git.untrack
    git rm --cached $argv
    commit untrack
    git add .
    git stash
    if confirm
        git pull
        git stash pop
        added | tee -a .git/info/exclude
        git reset
    end
end
