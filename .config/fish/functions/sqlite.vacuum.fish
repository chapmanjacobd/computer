# Defined interactively
function sqlite.vacuum --argument db
    set tmp_bak (mktemp -d)/(path basename $db)
    sqlite3 "$db" "VACUUM main INTO '$tmp_bak'" # or .backup
    and mv "$tmp_bak" $db
end
