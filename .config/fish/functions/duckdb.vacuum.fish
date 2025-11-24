# Defined via `source`
function duckdb.vacuum
    if test (count $argv) -ne 1
        echo "Usage: duckdb.vacuum <database_file>"
        return 1
    end

    set -l db_file $argv[1]
    set -l temp_file (mktemp -u).duckdb

    duckdb -c "
        ATTACH '$db_file' AS db1;
        ATTACH '$temp_file' AS db2;
        COPY FROM DATABASE db1 TO db2;
    "
    and mv $temp_file $db_file
end
