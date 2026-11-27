# Defined interactively
function files.count --wraps='fd'
    fd -tf . $argv | count
end
