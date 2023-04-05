# Defined via `source`
function similar_artist
    sqlite3 track_metadata.db ".param set :artist '$argv'" ".read check.sql"
end
