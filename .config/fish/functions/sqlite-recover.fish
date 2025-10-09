# Defined interactively
function sqlite-recover --argument db
    set tmp_bak (mktemp -d)/(path basename $db)
    sqlite3 "$db" ".recover" | sqlite3 "$tmp_bak"
    and mv "$tmp_bak" $db
end
