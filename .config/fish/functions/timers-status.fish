# Defined interactively
function timers-status
    for service in (systemctl --user list-timers --all --no-pager --no-legend --state=running | awk '{print $NF}')
        begin
            pstree -a -p (systemd-pid-u $service)
            timer-status $service
        end | less -FSRXc
    end
end
