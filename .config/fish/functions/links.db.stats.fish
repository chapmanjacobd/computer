# Defined interactively
function links.db.stats
    for s in ~/mc/*.db
        echo $s
        lb openlinks $s -L inf $argv -pa
    end
end
