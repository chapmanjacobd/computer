# Defined interactively
function sqlite-check
    sqlite3 $argv 'pragma integrity_check'
end
