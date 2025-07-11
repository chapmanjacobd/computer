# Defined interactively
function uptime_secs
    math -s0 (cat /proc/uptime | awk '{print $1}')
end
