# Defined interactively
function renamed
    git status --porcelain --short | awk '$1 == "R" {print $4}'
end
