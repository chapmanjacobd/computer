# Defined interactively
function gitls-commits
    git log --pretty=format: --name-only | sed '/^$/d' | asc
end
