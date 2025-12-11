# Defined interactively
function sqlite.group.by --argument db table column where
    if test -z "$where"
        set where "1=1"
    end

    sqlite3 $db "select $column, count(*) from $table where $where group by 1 order by 2"
end
