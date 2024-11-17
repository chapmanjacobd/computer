# Defined interactively
function tubeupdate
    for db in ~/lb/video.db ~/lb/audio.db ~/lb/tax_sounds.db ~/lb/tax.db
        lb dedupe-db $db playlists --bk extractor_playlist_id
        sleepy_run.py -- python -u -m xklb.lb tubeupdate $db
    end
end
