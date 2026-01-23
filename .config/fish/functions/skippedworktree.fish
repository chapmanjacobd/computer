# Defined interactively
function skippedworktree --wraps='git ls-files'
    git-ls-filter S $argv
end
