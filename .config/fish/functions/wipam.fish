# Defined interactively
function wipam
    git commit --amend -m (git log -1 --pretty=format:"%B")
    git push -f
end
