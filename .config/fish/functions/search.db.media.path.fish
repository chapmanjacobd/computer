# Defined interactively
function search.db.media.path --argument db q
    sqlite --no-headers --raw-lines $db "select path from media where path like '%$q%'"
end
