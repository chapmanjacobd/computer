# Defined interactively
function sqlite.tables
    for table in (sqlite-utils tables --tsv $argv | tail -n +2 | chars.no.quotes)
        if not string match -q '*_fts_*' $table; and not string match -q '*_fts' $table; and not string match -q sqlite_stat1 $table
            echo $table
        end
    end

end
