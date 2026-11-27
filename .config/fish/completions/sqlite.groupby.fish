complete -c sqlite.groupby -n '__fish_is_nth_token 2' -f -a '(sqlite.tables (commandline -opc)[2] 2>/dev/null)' -d 'Table'
complete -c sqlite.groupby -n '__fish_is_nth_token 3' -f -a '(sqlite.columns (commandline -opc)[2] (commandline -opc)[3] 2>/dev/null)' -d 'Column to group by'
complete -c sqlite.groupby -n '__fish_is_nth_token 4' -f -d 'WHERE clause (default: 1=1)'
