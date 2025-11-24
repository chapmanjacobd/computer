# Defined interactively
function files.ext.asc
    fd -tf -HI . $argv | ext | asc
end
