# Defined interactively
function modified-staged
    git status --porcelain --short | grep '^M ' | awk '$2 !~ /^\.\./ {print $2}'
end
