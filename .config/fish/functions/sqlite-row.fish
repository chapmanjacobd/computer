# Defined interactively
function sqlite-row --argument db table key value
    sqlite.utils rows "$db" "$table" --limit 10 --where "$key='$value'" | jq -r '.[] | to_entries[] | select(.value != null) | "\(.key) \(.value)"' | sort
end
