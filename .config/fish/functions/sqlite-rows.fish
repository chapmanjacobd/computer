# Defined interactively
function sqlite-rows --argument db key value
    sqlite-utils rows "$db" media --where "$key like '$value'" | jq -r '.[] | to_entries[] | select(.value != null) | "\(.key) \(.value)"' | sort --unique --ignore-case
end
