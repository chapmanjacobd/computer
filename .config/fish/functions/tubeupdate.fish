# Defined interactively
function tubeupdate
    for db in ~/lb/fs/video.db ~/lb/fs/audio.db ~/lb/fs/tax_sounds.db ~/lb/dl/tax.db
        lb dedupe-db $db playlists --bk extractor_playlist_id
        sleepy_run.py -- python -u -m library.lb tubeupdate $db
    end
end
