# Defined interactively
function lb-refresh
    lb fsadd ~/lb/video.db --video ~/d/sync/video/
    lb fsadd ~/lb/audio.db --audio ~/d/sync/audio/

    lb fsadd ~/lb/tax.db --video ~/d/sync/porn/video/
    lb fsadd ~/lb/tax_sounds.db --audio ~/d/sync/porn/audio/

    ~/lb/
    for db in video.db tax.db audio.db tax_sounds.db
        b sqlite-utils rebuild-fts $db media
    end
    wait
end
