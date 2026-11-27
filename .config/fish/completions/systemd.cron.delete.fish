complete -c systemd.cron.delete -f
complete -c systemd.cron.delete -n '__fish_is_nth_token 1' -a '(systemctl --user list-timers --all --no-pager --no-legend 2>/dev/null | string match -ra "[^ ]+[.]timer")' -d 'Timer unit'
