complete -c eval.par -n '__fish_is_nth_token 1' -f -a '(seq 1 (nproc))' -d 'Number of parallel jobs'
complete -c eval.par -n '__fish_is_nth_token 2' -a '(__fish_complete_command)' -d 'Command to run'
