# Defined interactively
function lb.refresh
    lb fsadd ~/lb/audio.db --audio ~/sync/audio/
    lb fsadd ~/lb/video.db --video ~/sync/video/

    lb fsadd ~/lb/tax.db --video ~/sync/porn/video/
    lb fsadd ~/lb/tax_sounds.db --audio ~/sync/porn/audio/
end
