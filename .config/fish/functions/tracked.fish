# Defined interactively
function tracked --wraps='git ls-files'
    git-ls-filter H $argv
end
