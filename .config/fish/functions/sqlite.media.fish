# Defined interactively
function sqlite.media --argument db key value
    sqlite-utils rows "$db" media --limit 1 --where "$key='$value'" | jq -r '.[] | to_entries[] | select(.value != null) | "\(.key) \(.value)"' | sort
end
