# Defined interactively
function chars.no.alpha
    grep -v -P '^[[:alpha:]]+$'
end
