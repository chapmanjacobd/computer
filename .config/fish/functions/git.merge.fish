function git.merge --wraps='git merge'
    git merge $argv
    and git branch --delete $argv
end
