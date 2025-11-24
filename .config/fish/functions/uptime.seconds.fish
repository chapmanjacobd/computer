# Defined interactively
function uptime.seconds
    math -s0 (cat /proc/uptime | awk '{print $1}')
end
