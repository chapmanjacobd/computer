# Defined interactively
function ps.paused
    ps --no-headers -weo pid,stat,command ww | awk '$2 ~ /^T/ { print $0 }' | string trim
end
