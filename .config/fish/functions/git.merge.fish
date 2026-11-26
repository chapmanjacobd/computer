function git.merge
    git merge $argv
    and git branch --delete $argv
end
