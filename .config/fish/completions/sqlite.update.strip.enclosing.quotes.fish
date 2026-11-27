function __fish_sqlite_update_strip_enclosing_quotes_columns
    set -l tokens (commandline -opc)
    set -l db $tokens[2]
    test -f "$db"; or return
    sqlite3 -batch -init /dev/null -noheader -list "$db" \
        "SELECT DISTINCT p.name FROM sqlite_master m, pragma_table_info(m.name) p WHERE m.type = 'table'" 2>/dev/null
end
complete -c sqlite.update.strip.enclosing.quotes -n 'test (count (commandline -opc)) -ge 2' -a '(__fish_sqlite_update_strip_enclosing_quotes_columns)' -d 'Column name'
