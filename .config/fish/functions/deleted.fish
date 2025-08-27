# Defined interactively
function deleted --wraps='git status'
    git status --porcelain --short $argv | awk '($1 == "D") && $2 !~ /^\.\./ {print $2}'
end
