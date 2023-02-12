# Defined via `source`
function dql
    sqlite-utils --no-headers --csv ~/lb/fs/d.db $argv | tr -d '\r'
end
