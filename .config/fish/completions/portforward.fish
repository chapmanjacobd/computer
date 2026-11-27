complete -c portforward -f
complete -c portforward -n '__fish_is_nth_token 1' -a '(__fish_print_hostnames)' -d 'Computer name'
