# Defined via `source`
function gitadded --wraps='git diff'
    git diff --name-status $argv | grep ^A | cut -f2
end
