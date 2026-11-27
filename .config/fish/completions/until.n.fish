complete -c until.n -n '__fish_is_nth_token 1' -f -d 'Number of attempts'
complete -c until.n -n '__fish_is_nth_token 2' -a '(__fish_complete_command)' -d 'Command to retry'
