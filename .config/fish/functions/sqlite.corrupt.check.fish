# Defined interactively
function sqlite.corrupt.check
    sqlite3 $argv 'pragma integrity_check'
end
