# Defined via `source`
function lines.no.empty --wraps='rg'
    rg -N "\S" $argv
end
