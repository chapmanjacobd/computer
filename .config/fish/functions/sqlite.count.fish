# Defined interactively
function sqlite.count --argument db table
    sqlite --raw-lines $db "select count(*) from $table"
end
