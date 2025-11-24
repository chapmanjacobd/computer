# Defined interactively
function chars.alpha
    grep -P '^[[:alpha:]]+$' $argv
end
