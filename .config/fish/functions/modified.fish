# Defined interactively
function modified -w 'git status'
    git status --porcelain --short | awk '$1 == "M" && $2 !~ /^\.\./ {print $2}'
end
