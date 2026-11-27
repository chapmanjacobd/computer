complete -c chain_one.py -f
complete -c chain_one.py -n '__fish_is_nth_token 1' -a '(__fish_complete_command)' -d 'First command to execute'
complete -c chain_one.py -n '__fish_is_nth_token 2' -a '(__fish_complete_command)' -d 'Second command if stdout is one line'
