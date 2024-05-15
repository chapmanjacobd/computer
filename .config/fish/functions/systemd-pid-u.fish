# Defined interactively
function systemd-pid-u
    systemctl --user show -p MainPID $argv | awk -F= '{print $2}'
end
