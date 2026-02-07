# Defined interactively
function links.db.stats
    for s in ~/mc/*.db
        echo $s
        lb fs $s -pa
    end
end
