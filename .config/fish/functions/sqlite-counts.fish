# Defined via `source`
function sqlite-counts --argument db table col
    set total (sqlite-count $db $table)

    set null (sqlite --raw-lines $db "select count(*) from $table where $col is null")
    printf 'NULL: %s (%s%%)\n' $null (percent $null $total)

    set zero (sqlite --raw-lines $db "select count(*) from $table where $col =0")
    printf '0: %s (%s%%)\n' $zero (percent $zero $total)

    set empty (sqlite --raw-lines $db "select count(*) from $table where $col =''")
    printf "'': %s (%s%%)\n" $empty (percent $empty $total)

    set values (math $total-$empty-$zero-$null)
    printf "values: %s (%s%%)\n" $values (percent $values $total)
end
