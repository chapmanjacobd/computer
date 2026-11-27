complete -c sshuttle.vpn.for -f
complete -c sshuttle.vpn.for -n '__fish_is_nth_token 1' -a '(__fish_print_hostnames)' -d 'SSH host'
complete -c sshuttle.vpn.for -n '__fish_is_nth_token 2' -a '(__fish_print_hostnames)' -d 'Destination host'
