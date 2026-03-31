# Defined interactively
function daily.links.extra
    for db in ~/mc/*.db ~/lb/sites/manual/pornolab.net.db
        command links open --prefix="https://www.google.com/search?q=" -R -m1 -L7 --db "$db" $argv
    end
end
