# Defined interactively
function lsd --wraps='fd'
    fd -d1 --full-path --absolute-path . $argv
end
