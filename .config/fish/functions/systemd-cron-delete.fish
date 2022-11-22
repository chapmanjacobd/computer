# Defined via `source`
function systemd-cron-delete --argument unit
    systemctl --user disable --now $unit.timer
    trash-put ~/.config/systemd/user/$unit.service
    trash-put ~/.config/systemd/user/$unit.timer
    systemctl --user list-timers --no-pager --all
end
