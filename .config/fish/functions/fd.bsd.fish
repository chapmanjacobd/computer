# Defined via `source`
function fd.bsd --wraps='fd'
    fd $argv --exec-batch printf '%s\n'
end
