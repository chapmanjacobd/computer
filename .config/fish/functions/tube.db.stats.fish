# Defined interactively
function tube.db.stats
    for db in $argv
        echo $db
        sqlite.utils $db -t 'select extractor_key, count(*) as count, hours_update_delay from playlists group by 1,3 order by hours_update_delay,count desc'
        echo
    end
end
