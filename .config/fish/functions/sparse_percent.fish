# Defined interactively
function sparse_percent
    find "$argv" -printf '%S\n' | percent_from_float
end
