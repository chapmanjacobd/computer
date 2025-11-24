# Defined interactively
function ps.resume.all
    for pid in (ps.paused | cut -d' ' -f1)
        ps.resume $pid
    end
end
