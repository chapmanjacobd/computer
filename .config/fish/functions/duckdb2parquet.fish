# Defined via `source`
function duckdb2parquet
    for s in $argv
        duckdb $s -c "EXPORT DATABASE '$s.parquet' (FORMAT 'parquet', COMPRESSION 'zstd', COMPRESSION_LEVEL 5, ROW_GROUP_SIZE 50_000);"
    end
end
