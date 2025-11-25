function systemd.cron
    # systemd.cron wakeup '*-*-* 9:30' lt.wakeup
    # hint: you can check if your systemd calendar argument likeso
    # systemd-analyze calendar "Mon..Fri *-*-* 10:00:00"
    # hint: also see timers-start, timers.stop, and timers-reset
    set unit $argv[1]
    set cal $argv[2]
    set cmd $argv[3..-1]

    echo "[Unit]
Description='On $cal run $cmd'

[Service]
Type=simple
RemainAfterExit=no
TimeoutStartSec=infinity
ExecStartPre=/bin/sleep 100
ExecStart='/usr/bin/fish' '-c' '$cmd'
" >~/.config/systemd/user/$unit.service

    echo "[Unit]
Description='On $cal run $cmd'

[Timer]
Persistent=yes
OnCalendar=$cal

[Install]
WantedBy=timers.target
" >~/.config/systemd/user/$unit.timer

    touch ~/.local/share/systemd/timers/stamp-$unit.timer
    systemctl --user daemon-reload
    systemctl --user enable --now $unit.timer
    systemctl --user list-timers --no-pager --all
end
