# Defined interactively
function untracked
    git status --untracked-files --porcelain --short | awk '($1 == "U" || $1 == "??") && $2 !~ /^\.\./ {print $2}'
end
