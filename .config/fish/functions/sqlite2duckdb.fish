# Defined via `source`
function sqlite2duckdb -a sqlite_db
    set duckdb_db (path change-extension duckdb $sqlite_db)

    duckdb -c "
        ATTACH '$sqlite_db' AS db1;
        ATTACH '$duckdb_db' AS db2;
        COPY FROM DATABASE db1 TO db2;
    "
end
