# Defined interactively
function git.copy
    ssh $argv "cd $(pwd); git diff" | git apply -
end
