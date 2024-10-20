# Defined interactively
function avg_size
    bytes (math -s0 "$(filesize)/$(fd -tf | count)")
end
