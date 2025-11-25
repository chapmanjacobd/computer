# Defined interactively
function search.db.playlists
    for db in $argv[2..-1]
        echo $db
        lb sdb $db playlists $argv[1]
    end
end
