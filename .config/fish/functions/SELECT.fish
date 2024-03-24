# Defined via `source`
function SELECT
    clickhouse local -q "SELECT $argv FORMAT Markdown"
end
