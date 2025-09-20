# Defined interactively
function gitcopystaged
    ssh $argv "cd $(pwd); git diff --staged" | git apply -
end
