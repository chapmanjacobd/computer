# Defined interactively
function untracked
    git status --porcelain --short | awk '$1 == "U" && $2 !~ /^\.\./ {print $2}'
end
