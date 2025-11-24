# Defined interactively
function sql.all
    for db in (fd -eDB . -HI)
        echo $db
        sqlite3 $db $argv
    end
end
