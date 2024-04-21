# Defined interactively
function lb-compress
    for db in $argv
        for table in media playlists
            sqlite-utils disable-fts $db $table
        end
        sqlite-utils drop-table $db sqlite_stat1

        sqlite-utils vacuum $db
    end
end
