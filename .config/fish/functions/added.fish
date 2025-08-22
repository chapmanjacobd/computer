# Defined via `source`
function added --wraps='git diff'
    git status --porcelain --short $argv | awk '($1 == "A") && $2 !~ /^\.\./ {print $2}'
end
