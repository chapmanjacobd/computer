complete -c ps.throttle -f
complete -c ps.throttle -s s -x -d 'Seconds to sleep after SIGSTOP (default: 10)'
complete -c ps.throttle -s a -x -d 'Seconds alive after SIGCONT (default: 5)'
complete -c ps.throttle -s v -d 'Print every signal sent'
complete -c ps.throttle -s h -d 'Show usage'
complete -c ps.throttle -a '(__fish_complete_pids)'
