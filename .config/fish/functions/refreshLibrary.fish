# Defined interactively
function refreshLibrary
    ~/lb/
    b lb fsupdate video.db
    b lb fsupdate fs/tax.db
    b lb fsupdate audio.db
    b lb fsupdate fs/63_Sounds.db
    wait
end
