# Defined interactively
function files.ext.asc
    fd -tf -HI . $argv | chars.ext | asc
end
