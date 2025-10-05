# Defined interactively
function sqlite-preview
    for db in $argv
        echo \#\# $db
        for table in (sqlite-tables "$db") (sqlite-views "$db")
            if not string match -q '*_fts_*' $table; and not string match -q '*_fts' $table; and not string match -q 'sqlite_*' $table
                echo \#\#\# $table \((sqlite-count "$db" "$table") rows\)
                lb tables "$db" -t "$table" -L 5
                echo
            end
        end
        echo
    end
end
