# Defined via `source`
function playlists
    for s in $argv
        sqlite --no-headers --raw-lines "$s" 'select path from playlists'
    end
end
