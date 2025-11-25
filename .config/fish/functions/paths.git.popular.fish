# Defined interactively
function paths.git.popular
    git log --pretty=format: --name-only | filter-empty-lines | asc
end
