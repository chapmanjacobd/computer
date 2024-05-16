# Defined interactively
function presume-all
    for pid in (ppaused | cut -d' ' -f1)
        presume $pid
    end
end
