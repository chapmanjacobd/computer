# Defined via `source`
function dsql
    sqlite-utils --no-headers --csv ~/lb/fs/d.db $argv | tr -d '\r'
end
