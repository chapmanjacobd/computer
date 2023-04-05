# Defined interactively
function sqlite-preview
    for db in $argv
        echo \#\# $db
        for table in (sqlite-tables "$db") (sqlite-views "$db")
            echo \#\#\# $table \((sqlite-count "$db" "$table") rows\)
            sqlite-utils rows --limit 5 --fmt github "$db" "$table"
            echo
        end
        echo
    end
end
