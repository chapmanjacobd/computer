complete -c sqlite.rows -n '__fish_is_nth_token 2' -f -a '(sqlite.tables (commandline -opc)[2] 2>/dev/null)' -d 'Table'
complete -c sqlite.rows -n '__fish_is_nth_token 3' -f -a '(sqlite.columns (commandline -opc)[2] (commandline -opc)[3] 2>/dev/null)' -d 'Column'
complete -c sqlite.rows -n '__fish_is_nth_token 4' -f -d 'LIKE pattern'
