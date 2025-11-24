# Defined interactively
function avg_size
    bytes (math -s0 "$(file.size)/$(fd -tf | count)")
end
