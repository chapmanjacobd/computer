# Defined interactively
function gitdiffdate
    git log -p --since="$argv"
end
