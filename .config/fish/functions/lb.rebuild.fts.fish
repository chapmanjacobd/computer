# Defined interactively
function lb.rebuild.fts
    for db in video.db tax.db audio.db tax_sounds.db
        b sqlite.utils rebuild-fts ~/lb/$db media
    end
    wait
end
