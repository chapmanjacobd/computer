# Defined via `source`
function lb.maintainence
    ~/lb/
    for db in video.db tax.db audio.db tax_sounds.db
        # sqlite3 $db 'delete from media where time_deleted>0'
        b lb optimize --fts ~/lb/fs/$db
    end
    wait
end
