# Defined interactively
function daily.links.extra
    for db in ~/mc/*.db ~/lb/sites/manual/pornolab.net.db
        lb openlinks --max-same-domain 1 "$db" -w 'play_count=0' -rs --browser
    end
end
