complete -c server.ssh -f
complete -c server.ssh -n '__fish_is_nth_token 1' -a '(__fish_print_hostnames)' -d 'Host'
complete -c server.ssh -n '__fish_is_nth_token 2' -a '(__fish_complete_command)' -d 'Remote command'
