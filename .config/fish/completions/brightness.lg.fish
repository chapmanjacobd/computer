complete -c brightness.lg -f
complete -c brightness.lg -n '__fish_is_nth_token 1' -a get -d 'Print current brightness'
complete -c brightness.lg -n '__fish_is_nth_token 1' -a set -d 'Set brightness percentage'
complete -c brightness.lg -n '__fish_is_nth_token 1' -a up -d 'Increase brightness'
complete -c brightness.lg -n '__fish_is_nth_token 1' -a down -d 'Decrease brightness'
complete -c brightness.lg -n '__fish_seen_subcommand_from set; and __fish_is_nth_token 2' -a '(seq 1 100)' -d 'Brightness percentage'
