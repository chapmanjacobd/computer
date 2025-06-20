# Defined interactively
function sparse_percent
    find $argv -type f -printf '%S\n' | per_line "math 1-" | percent_from_float
end
