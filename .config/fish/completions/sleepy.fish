complete -c sleepy -f
complete -c sleepy -l action -x -a 'sleep signal' -d 'Action to take after trigger'
complete -c sleepy -s T -l time -x -d 'Seconds to sleep'
complete -c sleepy -s s -l signal -x -a 'SIGTERM SIGINT SIGHUP SIGKILL SIGUSR1 SIGUSR2' -d 'Exit signal to send'
complete -c sleepy -l raise-killed-signal -d 'Raise the expected non-zero signal'
complete -c sleepy -s t -l trigger -r -d 'Error message to monitor for'
complete -c sleepy -n '__fish_is_nth_token 1' -a '(__fish_complete_command)' -d 'Program command'
