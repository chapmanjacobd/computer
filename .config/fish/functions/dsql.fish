# Defined via `source`
function dsql
    for db in ~/lb/fs/d*.db
        lb fs "$db" -pf -s "$argv"
    end
end
