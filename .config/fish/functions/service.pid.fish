# Defined interactively
function service.pid -w 'systemctl --user show'
    systemctl --user show -p MainPID $argv | awk -F= '{print $2}'
end
