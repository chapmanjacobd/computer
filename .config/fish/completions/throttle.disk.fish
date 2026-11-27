complete -c throttle.disk -n '__fish_is_nth_token 1' -a '(__fish_complete_directories)' -d 'Mountpoint'
complete -c throttle.disk -n 'not __fish_is_nth_token 1' -f -a '(__fish_complete_command)' -d 'Command'
