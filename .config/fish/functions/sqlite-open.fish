# Defined interactively
function sqlite-open
    dbeaver-ce -con 'driver=SQLite|database='(path resolve $argv)
end
