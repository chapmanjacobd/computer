# Defined interactively
function dbs
    for db in ~/lb/fs/63_Sounds.db ~/lb/video.db ~/lb/fs/tax.db ~/lb/fs/91_New_Art.db ~/lb/audio.db ~/lb/fs/61_Photos_Unsorted.db
        echo $db
        $argv $db
    end
end
