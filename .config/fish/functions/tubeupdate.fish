# Defined interactively
function tubeupdate
    for db in ~/lb/video.db ~/lb/audio.db ~/lb/fs/63_Sounds.db ~/lb/tax.db
        lb dedupe-db $db playlists --bk extractor_playlist_id
        lb tubeupdate $db
    end
end
