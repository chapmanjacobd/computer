# Defined interactively
function paths.git.ls.deleted
    git log --all --pretty=format: --name-only --diff-filter=D $argv
end
