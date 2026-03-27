# Defined interactively
function go.release
    git push
    git tag -a $argv && git push --tags
end
