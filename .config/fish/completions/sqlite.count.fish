complete -c sqlite.count -n '__fish_is_nth_token 2' -f -a '(sqlite.tables (commandline -opc)[2] 2>/dev/null)' -d 'Table'
