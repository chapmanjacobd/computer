# Defined interactively
function userpids
    ps -o pid ww | tail -n +2 | string trim
end
