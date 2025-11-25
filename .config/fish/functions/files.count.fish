# Defined interactively
function files.count
    fd -tf . $argv | count
end
