# Defined interactively
function sqlite.group.by --argument db table column
    sqlite3 $db "select $column, count(*) from $table group by 1 order by 2"
end
