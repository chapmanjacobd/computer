# Defined interactively
function userd.pid
    systemctl --user show -p MainPID $argv | awk -F= '{print $2}'
end
