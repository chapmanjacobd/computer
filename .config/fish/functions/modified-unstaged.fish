# Defined interactively
function modified-unstaged
    git status --porcelain --short | grep '^ M' | awk '$2 !~ /^\.\./ {print $2}'
end
