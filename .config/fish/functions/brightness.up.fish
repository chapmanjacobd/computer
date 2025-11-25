# Defined interactively
function brightness.up
    if test pakon = (hostname)
        brightness.lg.up
    else
        brightness.set (math (brightness.get)+(brightness.step))
    end
end
