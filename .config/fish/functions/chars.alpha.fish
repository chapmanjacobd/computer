# Defined interactively
function chars.alpha --wraps='grep'
    grep -P '^[[:alpha:]]+$' $argv
end
