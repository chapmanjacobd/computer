# Defined interactively
function gitcopy
    ssh $argv "cd $(pwd); git diff" | git apply -
end
