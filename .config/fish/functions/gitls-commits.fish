# Defined interactively
function gitls-commits
    git log --pretty=format: --name-only | filter-empty-lines | asc
end
