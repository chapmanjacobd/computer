# Defined interactively
function service.pid
    systemctl --user show -p MainPID $argv | awk -F= '{print $2}'
end
