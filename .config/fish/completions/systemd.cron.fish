complete -c systemd.cron -n '__fish_is_nth_token 1' -f -d 'Unit name'
complete -c systemd.cron -n '__fish_is_nth_token 2' -f -a 'daily weekly hourly monthly' -d 'OnCalendar expression'
complete -c systemd.cron -n '__fish_is_nth_token 3' -f -a '(__fish_complete_command)' -d 'Command to run'
