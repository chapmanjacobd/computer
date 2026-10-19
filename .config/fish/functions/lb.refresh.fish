# Defined interactively
function lb.refresh
    lb db add fs ~/lb/audio.db --audio ~/sync/audio/
    lb db add fs ~/lb/video.db --video ~/sync/video/

    lb db add fs ~/lb/tax.db --video ~/sync/porn/video/
    lb db add fs ~/lb/tax_sounds.db --audio ~/sync/porn/audio/
end
