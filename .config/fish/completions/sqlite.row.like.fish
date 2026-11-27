complete -c sqlite.row.like -n '__fish_is_nth_token 2' -f -a '(sqlite.columns (commandline -opc)[2] media 2>/dev/null)' -d 'media column'
complete -c sqlite.row.like -n '__fish_is_nth_token 3' -f -d 'LIKE pattern'
