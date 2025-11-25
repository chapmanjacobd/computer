# Defined interactively
function brightness.down
    if test pakon = (hostname)
        brightness.lg.down
    else
        brightness.set (math "$(brightness.get)-(3*$(brightness.step))")
    end
end
