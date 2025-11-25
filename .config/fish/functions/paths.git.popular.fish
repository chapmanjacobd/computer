# Defined interactively
function paths.git.popular
    git log --pretty=format: --name-only | lines.not.empty | asc
end
