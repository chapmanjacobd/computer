# Defined interactively
function lb-refresh
    ~/lb/
    for db in video.db tax.db audio.db tax_Sounds.db
        lb fsupdate --delete-unplayable $db
        b sqlite-utils rebuild-fts $db media
    end
    wait
end
