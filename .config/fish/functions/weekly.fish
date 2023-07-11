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

    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/audio.db ~/lb/reddit/81_New_Music.db ~/lb/reddit/83_ClassicalComposers.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/video.db ~/lb/reddit/71_Mealtime_Videos.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/fs/63_Sounds.db ~/lb/reddit/63_Sounds.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/fs/tax.db ~/lb/reddit/69_Taxes.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/fs/61_Photos_Unsorted.db ~/lb/reddit/61_Photos_Unsorted.db

    for dfolder in 61_Photos_Unsorted 91_New_Art 95_Memes
        ~/d/$dfolder/
        gallery-dl --input-file (sed 's|^|https://www.instagram.com/\0|' ~/mc/$dfolder-instagram.txt | shuf | head -20 | psub)
    end

    dbackups
end
