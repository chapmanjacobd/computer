# Defined interactively
function dbs
    for db in ~/lb/tax_sounds.db ~/lb/video.db ~/lb/tax.db ~/lb/fs/91_New_Art.db ~/lb/audio.db ~/lb/fs/61_Photos_Unsorted.db
        echo $db
        $argv $db
    end
end
