# Defined interactively
function refreshLibrary
    ~/lb/
    for db in video.db fs/tax.db audio.db fs/63_Sounds.db
        lb fsupdate $db --delete-unplayable
        b sqlite-utils rebuild-fts $db media
    end
    wait
end
