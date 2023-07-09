# Defined via `source`
function sqlite-counts --argument db table col
    set total (sqlite-count $db $table)

    set null (sqlite --raw-lines $db "select count(*) from $table where $col is null")
    printf '%s is null: %s (%s%%)\n' $col $null (percent $null $total)

    set zero (sqlite --raw-lines $db "select count(*) from $table where $col =0")
    printf '%s=0: %s (%s%%)\n' $col $zero (percent $zero $total)

    set empty (sqlite --raw-lines $db "select count(*) from $table where $col =''")
    printf "%s='': %s (%s%%)\n" $col $empty (percent $empty $total)

    set total (sqlite --raw-lines $db "select count(*) from $table")
    printf "%s values: %s\n" $col (math $total-$empty-$zero-$null)
end
