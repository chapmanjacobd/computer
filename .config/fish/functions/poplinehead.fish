# Defined via `source`
function poplinehead
    head -n1 "$argv"
    sed -i 1d "$argv"
end
