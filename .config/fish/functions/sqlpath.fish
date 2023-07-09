# Defined interactively
function sqlpath --argument db q
    sqlite --no-headers --raw-lines $db "select path from media where path like '%$q%'"
end
