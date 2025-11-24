# Defined interactively
function sqlite.row.like --argument db key value
    sqlite-utils rows "$db" media --limit 10 --where "$key like '%$value%'" | jq -r '.[] | to_entries[] | select(.value != null) | "\(.key) \(.value)"' | sort
end
