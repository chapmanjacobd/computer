# Defined interactively
function commit --wraps='git'
    if count $argv >/dev/null
        git utccommit -m "$argv"
    else
        git utccommit
    end
end
