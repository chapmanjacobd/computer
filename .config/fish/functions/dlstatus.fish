# Defined via `source`
function dlstatus
    for db in ~/lb/audio.db ~/lb/video.db ~/lb/reddit/*db
        echo $db
        lb ds $argv $db
    end
end
