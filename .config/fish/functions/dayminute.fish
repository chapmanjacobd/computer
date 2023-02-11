# Defined interactively
function dayminute
    math -s 0 (date -d "1970-01-01 UTC $(date +%T)" +%s)'/60'
end
