# Defined interactively
function sparse_percent
    math 1-(find "$argv" -printf '%S\n') | percent_from_float
end
