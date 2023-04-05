# Defined interactively
function sqlite-preview
    for db in $argv
        echo $db
        for table in (sqlite-tables "$db")
            echo $table
            sqlite-utils rows --limit 5 --fmt github "$db" "$table"
        end
    end
end
