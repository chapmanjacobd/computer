# Defined via `source`
function sqlite.to.duckdb -a sqlite_db
    set duckdb_db (path change-extension duckdb $sqlite_db)

    duckdb -c "
        SET sqlite_all_varchar=true;

        ATTACH '$sqlite_db' AS db1;
        ATTACH '$duckdb_db' AS db2;
        COPY FROM DATABASE db1 TO db2;
    "
end
