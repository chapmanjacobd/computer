# Defined interactively
function sqlite-columns-counts --argument db table
    echo "## $db -- $table"
    echo
    for col in (sqlite-columns $db $table)
        echo "### $col"
        sqlite-counts $db $table $col
        echo
    end
end
