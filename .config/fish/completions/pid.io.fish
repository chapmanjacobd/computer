complete -c pid.io -f
complete -c pid.io -s d -l interval -x -d 'Interval between updates (default: 2)'
complete -c pid.io -l init-bias -x -d 'Number of intervals to rely on initial stats (default: 6)'
complete -c pid.io -n '__fish_is_nth_token 1' -a '(__fish_complete_pids)' -d 'PID of the process'
