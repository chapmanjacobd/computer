# Defined interactively
function sqlite-recover --argument db
    set tmp_bak (mktemp -d)/(path basename $db | path change-extension .db)
    sqlite3 -init /dev/null "$db" ".recover" | sqlite3 -init /dev/null "$tmp_bak"
    mv "$tmp_bak" $db
end
