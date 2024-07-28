# Defined interactively
function checkdb
    for db in $argv
        echo $db
        sqlite3 $db 'PRAGMA quick_check'
    end
end
