# Defined interactively
function sqlite-preview
    for db in $argv
        echo \#\# $db
        for table in (sqlite-tables "$db") (sqlite-views "$db")
            if not string match '*_fts_*' $table; and not string match '*_fts' $table; and not string match 'sqlite_stat1' $table
                echo \#\#\# $table \((sqlite-count "$db" "$table") rows\)
                sqlite-utils rows --limit 5 --fmt github "$db" "$table"
                echo
            end
        end
        echo
    end
end
