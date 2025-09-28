# Defined interactively
function modified.lines --wraps='git diff'
    git diff --numstat HEAD $argv | awk '$1 != 0 && $2 != 0 {print $3}'
end
