# Defined via `source`
function sqlite2duckdb -a sqlite_db -a duckdb_db
    duckdb -c "
        ATTACH '$sqlite_db' AS db1;
        ATTACH '$duckdb_db' AS db2;
        COPY FROM DATABASE db1 TO db2;
    "
end
