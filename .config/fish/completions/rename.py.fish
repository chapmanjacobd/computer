complete -c rename.py -n '__fish_is_nth_token 1' -f -d 'Search regex'
complete -c rename.py -n '__fish_is_nth_token 2' -f -d 'Replacement string'
complete -c rename.py -n 'not __fish_is_nth_token 1; and not __fish_is_nth_token 2' -F -d Path
