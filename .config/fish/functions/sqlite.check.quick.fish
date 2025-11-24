# Defined interactively
function sqlite.check.quick
    for db in $argv
        echo $db
        sqlite3 $db 'PRAGMA quick_check'
    end
end
