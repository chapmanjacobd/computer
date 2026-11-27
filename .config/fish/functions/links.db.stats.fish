# Defined interactively
function links.db.stats --wraps='lb'
    for s in ~/mc/*.db
        echo $s
        lb links open $s -L inf $argv -pa
    end
end
