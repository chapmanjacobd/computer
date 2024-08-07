# Defined interactively
function sqlite-drop-indexes --argument db
    for index in (sqlite indexes $db | jq -r '.[].index_name' | grep ^idx_ | strip_quotes)
        sqlite $db "drop index $index"
    end
end
