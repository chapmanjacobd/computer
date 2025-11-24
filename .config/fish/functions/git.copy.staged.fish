# Defined interactively
function git.copy.staged
    ssh $argv "cd $(pwd); git diff --staged" | git apply -
end
