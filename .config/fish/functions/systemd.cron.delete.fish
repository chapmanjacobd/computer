# Defined via `source`
function systemd.cron.delete --argument unit
    systemctl --user disable --now $unit.timer
    trash ~/.config/systemd/user/$unit.service
    trash ~/.config/systemd/user/$unit.timer
    systemctl --user list-timers --no-pager --all
end
