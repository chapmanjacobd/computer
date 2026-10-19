# Defined interactively
function search.db.media
    for db in $argv[2..-1]
        echo $db
        lb database search $db media $argv[1]
    end
end
