# Defined via `source`
function mv-by-filename-yearmonth
    while read line
        set date_str (date --date=(lb date $line) +%Y-%m)

        lb mv $line (parentname (path resolve $line))_$date_str/
    end
end
