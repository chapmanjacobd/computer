complete -c sqlite.column.counts -n '__fish_is_nth_token 1' -a '*.db *.sqlite *.sqlite3'
complete -c sqlite.column.counts -n '__fish_is_nth_token 2' -a '(sqlite.utils tables --columns (commandline -opc)[-1] 2>/dev/null | jq -r ".[].table")' -d 'Table'
complete -c sqlite.column.counts -n '__fish_is_nth_token 3' -a '(sqlite.columns (commandline -opc)[-2] (commandline -opc)[-1] 2>/dev/null)' -d 'Column'
