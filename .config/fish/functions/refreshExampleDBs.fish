# Defined via `source`
function refreshExampleDBs
    ~/lb/
    lb ta examples/mealtime.tw.db (cat ~/mc/71_Mealtime_Videos.txt)
    lb ta examples/podcasts.tl.db (cat ~/mc/82_Audiobooks.txt)
    lb ta examples/free-yt-movies.tw.db (cat ~/mc/75_MovieQueue.txt)
    # lb ta examples/music.tl.db (grep -v bandcamp ~/mc/81_New_Music.txt)
    lb ta examples/classical_music.tl.db (cat ~/mc/83_ClassicalComposers.txt)
    for db in ~/lb/examples/*.db
        sqlite-utils disable-fts $db media
        sqlite-utils vacuum $db
    end
    # git reset && git add examples/*.db && git commit -m 'sync example dbs' && git pull && git push
end
