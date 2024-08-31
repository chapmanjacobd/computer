# Defined interactively
function non_alpha
    grep -v -P '^[[:alpha:]]+$'
end
