# Defined in /home/xk/.config/fish/functions/sqlite.check.quick.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function sqlite.check
    for db in $argv
        echo $db
        sqlite3 $db 'PRAGMA integrity_check'
    end
end
