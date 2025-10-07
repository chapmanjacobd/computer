# Defined interactively
function tubeupdate
    for db in ~/lb/dl/video.db ~/lb/dl/audio.db ~/lb/dl/tax_sounds.db ~/lb/dl/tax.db
        lb dedupe-db $db playlists --bk extractor_playlist_id
        sleepy_run.py -- python -u -m library.lb tubeupdate $db
    end
end
