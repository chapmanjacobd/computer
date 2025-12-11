# Defined interactively
function go.release
    git tag -a $argv && git push --tags
end
