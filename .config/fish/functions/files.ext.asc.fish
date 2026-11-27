# Defined interactively
function files.ext.asc --wraps='fd'
    fd -tf -HI . $argv | chars.ext | asc
end
