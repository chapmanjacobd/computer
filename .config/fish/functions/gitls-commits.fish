# Defined interactively
function gitls1-commits
    git log --pretty=format: --name-only | filter-empty-lines | asc
end
