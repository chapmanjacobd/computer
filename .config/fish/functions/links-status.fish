# Defined interactively
function links-status
    for db in $argv
        echo $db
        lb openlinks $db -pa
    end
end
