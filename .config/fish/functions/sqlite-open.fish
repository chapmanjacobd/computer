# Defined interactively
function sqlite-open
    for f in $argv
        dbeaver-ce -con 'driver=SQLite|database='(path resolve $f)
    end
end
