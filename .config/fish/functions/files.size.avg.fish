# Defined interactively
function files.size.avg
    bytes (math -s0 "$(file.size)/$(fd -tf | count)")
end
