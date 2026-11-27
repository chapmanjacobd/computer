complete -c sqlite.groupby.words -f
complete -c sqlite.groupby.words -n '__fish_is_nth_token 1' -a '(__fish_complete_suffix .db .sqlite .sqlite3)' -d 'Database'
complete -c sqlite.groupby.words -n '__fish_is_nth_token 2' -a '(sqlite3 (commandline -opc)[-1] ".tables" 2>/dev/null | string split " ")' -d 'Table'
