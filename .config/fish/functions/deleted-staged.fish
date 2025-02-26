# Defined interactively
function deleted-staged
    git status --porcelain --short | grep '^D ' | awk '$2 !~ /^\.\./ {print $2}'
end
