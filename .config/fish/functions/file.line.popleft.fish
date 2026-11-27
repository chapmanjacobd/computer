# Defined via `source`
function file.line.popleft --wraps='head'
    head -n1 "$argv"
    sed -i 1d "$argv"
end
