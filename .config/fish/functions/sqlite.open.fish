# Defined interactively
function sqlite.open
    run dbeaver-ce -con 'driver=SQLite|database='(path resolve $argv[1])
    sleep 2

    for f in $argv[2..-1]
        dbeaver-ce -con 'driver=SQLite|database='(path resolve $f)
    end
end
