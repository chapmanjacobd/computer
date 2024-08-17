# Defined interactively
function created
    git status --porcelain --short | awk '$1 == "A" && $2 !~ /^\.\./ {print $2}'
end
