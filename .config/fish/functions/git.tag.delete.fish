# Defined interactively
function git.tag.delete --wraps='git tag -d'
    git tag --delete $argv
    git push origin :refs/tags/$argv
end
