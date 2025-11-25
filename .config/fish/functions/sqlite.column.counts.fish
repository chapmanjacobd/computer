# Defined via `source`
function sqlite.column.counts --argument db table col
    set total (sqlite-count $db $table)

    set null (sqlite --raw-lines $db "select count(*) from $table where $col is null")
    set zero (sqlite --raw-lines $db "select count(*) from $table where $col =0")
    set empty (sqlite --raw-lines $db "select count(*) from $table where $col =''")
    set values (math $total-$empty-$zero-$null)

    printf "values: %s (%s%%)\n" $values (percent $values $total)
    printf 'NULL: %s (%s%%)\n' $null (percent $null $total)
    printf '0: %s (%s%%)\n' $zero (percent $zero $total)
    printf "'': %s (%s%%)\n" $empty (percent $empty $total)
end
