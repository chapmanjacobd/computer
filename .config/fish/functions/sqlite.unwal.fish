# Defined interactively
function sqlite.unwal
    sqlite3 $argv 'PRAGMA wal_checkpoint(TRUNCATE);'
end
