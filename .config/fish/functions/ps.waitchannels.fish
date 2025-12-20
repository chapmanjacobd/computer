# Defined interactively
function ps.waitchannels
    ps -eo wchan= | asc
end
