# Defined via `source`
function dsql
    for db in ~/lb/fs/d*.db
        sqlite-utils --no-headers --csv $db "$argv" | tr -d '\r'
    end
end
