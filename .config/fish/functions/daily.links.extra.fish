# Defined interactively
function daily.links.extra
    for db in ~/mc/*.db
        lb openlinks --max-same-domain 2 "$db" -w 'play_count=0' -rs --browser
    end
end
