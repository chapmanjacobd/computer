# Defined interactively
function git.tag.delete
    git tag --delete $argv
    git push --delete :refs/tags/$argv
end
