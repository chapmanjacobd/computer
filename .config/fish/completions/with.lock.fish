complete -c with.lock -n '__fish_is_nth_token 1' -f -d 'Lock name'
complete -c with.lock -n '__fish_is_nth_token 2' -f -a '(__fish_complete_command)' -d 'Command to run under the lock'
