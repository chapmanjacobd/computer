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

    ~/j/computing/
    reddit-user-to-sqlite user BuonaparteII
    for title in (sqlite --no-headers --raw-lines ~/d/30_Computing/reddit.db 'select permalink from comments' | sed 's|.*\/comments\/[^\/]*\/\(.*\)/.*|\1|' | tr / '#')
        set comment_id (string split '#' -f2 $title)
        sqlite --no-headers --raw-lines ~/d/30_Computing/reddit.db "select text from comments where permalink like '%$comment_id%'" > $title.md
    end
    for title in (sqlite --no-headers --raw-lines ~/d/30_Computing/reddit.db 'select permalink from posts' | sed 's|.*\/comments\/[^\/]*\/\(.*\)/.*|\1|')
        sqlite --no-headers --raw-lines ~/d/30_Computing/reddit.db "select text from posts where permalink like '%$title%' order by timestamp desc limit 1" > $title.md
    end
    fd -S-12b -tf -x rm
    lb mergedbs --pk id ~/d/30_Computing/BuonaparteII.db ~/d/30_Computing/reddit.db

    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/audio.db ~/lb/reddit/81_New_Music.db ~/lb/reddit/83_ClassicalComposers.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/video.db ~/lb/reddit/71_Mealtime_Videos.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/fs/63_Sounds.db ~/lb/reddit/63_Sounds.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/fs/tax.db ~/lb/reddit/69_Taxes.db

    ~/lb/
    for db in reddit/61_Photos_Unsorted.db
        lb redditupdate $db --lookback 8
    end
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/fs/61_Photos_Unsorted.db ~/lb/reddit/61_Photos_Unsorted.db

    for dfolder in 61_Photos_Unsorted 91_New_Art 95_Memes
        ~/d/$dfolder/
        gallery-dl --input-file (sed 's|^|https://www.instagram.com/\0|' ~/mc/$dfolder-instagram.txt | shuf | head -20 | psub)
    end

    dbackups
end
