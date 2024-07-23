# Defined interactively
function lb-refresh
    lb fsadd ~/lb/audio.db --audio ~/d/sync/audio/
    lb fsadd ~/lb/video.db --video ~/d/sync/video/

    lb fsadd ~/lb/tax.db --video ~/d/sync/porn/video/
    lb fsadd ~/lb/tax_sounds.db --audio ~/d/sync/porn/audio/
end
