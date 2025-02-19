# Defined interactively
function gitdiffdate
    git log --pretty=format:"%ad %an %h %B%-C()" --since="$argv" | less -S
    git diff --no-textconv (git rev-list -n 1 --before="$argv" HEAD)
end
