# Defined interactively
function daily.links.extra
    for db in ~/mc/*.db ~/lb/sites/manual/pornolab.net.db
        command links open -R -m1 -L7 --db "$db"
    end
end
