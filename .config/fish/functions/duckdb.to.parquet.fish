# Defined via `source`
function duckdb.to.parquet
    for s in $argv
        duckdb $s -c "SET sqlite_all_varchar=true;EXPORT DATABASE '$s.parquet' (FORMAT 'parquet', COMPRESSION 'zstd', COMPRESSION_LEVEL 5, ROW_GROUP_SIZE 50_000, ROW_GROUPS_PER_FILE 200);"
    end
end
