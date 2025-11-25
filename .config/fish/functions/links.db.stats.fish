# Defined interactively
function links.db.stats
    for db in $argv
        echo $db
        lb openlinks $db -pa
    end
end
