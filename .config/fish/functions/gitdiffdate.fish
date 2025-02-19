# Defined interactively
function gitdiffdate
    git log --pretty=format:"%ad %an %h %B%-C()" --since="$argv" | less
    git diff (git rev-list -n 1 --before="$argv" HEAD)
end
