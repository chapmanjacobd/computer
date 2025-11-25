# Defined interactively
function sqlite.rows --argument db table key value
    sqlite.utils rows "$db" $table --where "$key like '$value'" | jq -r '.[] | to_entries[] | select(.value != null) | "\(.key) \(.value)"' | sort --unique --ignore-case
end
