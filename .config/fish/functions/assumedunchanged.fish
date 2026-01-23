# Defined interactively
function assumedunchanged --wraps='git ls-files'
    git-ls-filter h $argv
end
