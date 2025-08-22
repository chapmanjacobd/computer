# Defined interactively
function deleted --wraps='git diff'
    git status --porcelain --short $argv | awk '($1 == "D") && $2 !~ /^\.\./ {print $2}'
end
