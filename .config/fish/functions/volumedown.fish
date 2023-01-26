# Defined interactively
function volumedown
    if pgrep -f catt
        catt volumedown 3
    else
        vol -3
    end
end
