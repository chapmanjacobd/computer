# Defined interactively
function sqlite-count --argument db table
    sqlite-utils --csv "$db" "select count(*) count from $table" | tail -n +2
end
