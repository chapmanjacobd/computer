# Defined interactively
function sqlgrep_playlists
    for db in $argv[2..-1]
        echo $db
        lb sdb $db playlists $argv[1]
    end
end
