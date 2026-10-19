# Defined interactively
function tubeupdate
    for db in ~/lb/dl/video.db ~/lb/dl/audio.db ~/lb/dl/tax_sounds.db ~/lb/dl/tax.db
        lb database dedupe $db playlists --bk extractor_playlist_id
        sleepy -- python -u -m library database update video $db
    end
end
