# Defined via `source`
function lb-maintainence
    ~/lb/
    for db in video.db fs/tax.db audio.db fs/63_Sounds.db
        sqlite3 $db 'delete from media where time_deleted>0'
        b lb optimize --fts $db
    end
    wait
end
