# Defined interactively
function sqlall
    for db in (fd -eDB . -HI)
        echo $db
        sqlite3 $db $argv
    end
end
