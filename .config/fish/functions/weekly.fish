function weekly
    trash ~/d/.stversions/*

    mrmusic
    #mrvideo
    mrporn
    mrrelax
    morganize

    pip install --upgrade yt-dlp gallery-dl praw xklb

    tubeupdate
    #dla
    wait

    ~/lb/
    for db in reddit/61_Photos_Unsorted.db
        lb redditupdate $db --lookback 8
    end

    lb mergedbs --pk path --only-target-columns --ignore -t media ~/lb/audio.db ~/lb/reddit/81_New_Music.db ~/lb/reddit/83_ClassicalComposers.db
    lb mergedbs --pk path --only-target-columns --ignore -t media ~/lb/video.db ~/lb/reddit/71_Mealtime_Videos.db
    lb mergedbs --pk path --only-target-columns --ignore -t media ~/lb/fs/63_Sounds.db ~/lb/reddit/63_Sounds.db
    lb mergedbs --pk path --only-target-columns --ignore -t media ~/lb/fs/tax.db ~/lb/reddit/69_Taxes.db
    lb mergedbs --pk path --only-target-columns --ignore -t media ~/lb/fs/61_Photos_Unsorted.db ~/lb/reddit/61_Photos_Unsorted.db

    for folder in 61_Photos_Unsorted
        ~/d/$folder/
        gallery-dl --input-file ~/mc/$folder.txt
    end

    # dbackups
end
