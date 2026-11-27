# Defined interactively
function paths.git.ls.deleted --wraps='git'
    git log --all --pretty=format: --name-only --diff-filter=D $argv
end
