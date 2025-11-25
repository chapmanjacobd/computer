# Defined interactively
function sqlite-columns --argument db table
    sqlite-utils tables --columns "$db" | jq -r ".[] | select(.table == \"$table\").columns | join(\"\n\")" | chars.no.quotes
end
