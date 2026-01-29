# Defined interactively
function git.rm.staged
    git diff --cached | git apply --reverse
end
