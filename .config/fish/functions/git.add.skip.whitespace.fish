# Defined interactively
function git.add.skip.whitespace
    git diff --ignore-all-space | git apply --cached
end
