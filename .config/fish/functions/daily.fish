function daily
    ~/
    sed -i '$ d' ~/.gitignore
    sed -i '$ d' ~/j/.gitignore

    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files backup:.local/Downloads/. ~/d/75_MovieQueue/
    lb relmv /mnt/d/70_Now_Watching/Keep/* /mnt/d/77_Library/

    catt volume 0 && catt volume 40
    pip install --upgrade gallery-dl pychromecast
    for dfolder in 61_Photos_Unsorted 91_New_Art 95_Memes
        ~/d/$dfolder/
        gallery-dl --input-file (sed 's|^|https://www.instagram.com/\0|' ~/mc/$dfolder-instagram.txt | shuf | head -20 | psub)
    end

    for db in ~/lb/reddit/*.db
        lb redditupdate $db --lookback 2
    end

    lb hnadd --oldest ~/lb/hackernews/hn.db

    ~
    sync_history
    # command trash-empty 10 -f
    lbdl ~/lb/audio.db --audio --prefix /mnt/d/81_New_Music/

    if not pgrep ffmpeg >/dev/null
        ~/d/69_Taxes_Keep/ && ffsmallpar
    end

    lb mergedbs --pk path --only-target-columns --ignore -t media ~/lb/audio.db ~/lb/reddit/81_New_Music.db ~/lb/reddit/83_ClassicalComposers.db
    lb mergedbs --pk path --only-target-columns --ignore -t media ~/lb/video.db ~/lb/reddit/71_Mealtime_Videos.db
    lb mergedbs --pk path --only-target-columns --ignore -t media ~/lb/fs/63_Sounds.db ~/lb/reddit/63_Sounds.db
    lb mergedbs --pk path --only-target-columns --ignore -t media ~/lb/fs/tax.db ~/lb/reddit/69_Taxes.db
    lb mergedbs --pk path --only-target-columns --ignore -t media ~/lb/fs/61_Photos_Unsorted.db ~/lb/reddit/61_Photos_Unsorted.db
end
