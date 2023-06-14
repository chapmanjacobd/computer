# Defined via `source`
function sqlite-counts --argument db table col

    set null (sqlite --raw-lines $db        "select count(*) from $table where $col is null")
    printf '%s is null: %s\n' $col $null

    set zero (sqlite --raw-lines $db "select count(*) from $table where $col =0")
    printf '%s=0: %s\n' $col $zero

    set empty (sqlite --raw-lines $db "select     count(*) from $table where $col =''")
    printf "%s='': %s\n" $col $empty

    set total (sqlite --raw-lines $db "select count(*) from $table")
    printf "%s values: %s\n" $col (math $total-$empty-$zero-$null)
end
