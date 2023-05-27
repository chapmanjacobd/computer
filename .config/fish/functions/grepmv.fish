# Defined via `source`
function grepmv
    mkdir -p "$argv[2]"
    mv (rg -i --files-with-matches "$argv[1]") "$argv[2]"
end
