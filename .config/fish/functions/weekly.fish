function weekly
    dbackups
    trash ~/d/sync/.stversions/*

    mrmusic
    #mrvideo
    mrporn
    #mrrelax
    morganize

    mam_update

    lb-refresh

    pip install --upgrade yt-dlp gallery-dl praw xklb

    ~/d/library/datasets/social/
    reddit-user-to-sqlite user BuonaparteII
    ~/j/social/
    for title in (sqlite --no-headers --raw-lines ~/d/library/datasets/social/reddit.db 'select permalink from comments' | sed 's|.*\/comments\/[^\/]*\/\(.*\)/.*|\1|' | tr / '#')
        set comment_id (string split '#' -f2 $title)
        sqlite --no-headers --raw-lines ~/d/library/datasets/social/reddit.db "select text from comments where permalink like '%$comment_id%'" >$title.md
    end
    for title in (sqlite --no-headers --raw-lines ~/d/library/datasets/social/reddit.db 'select permalink from posts' | sed 's|.*\/comments\/[^\/]*\/\(.*\)/.*|\1|')
        sqlite --no-headers --raw-lines ~/d/library/datasets/social/reddit.db "select text from posts where permalink like '%$title%' order by timestamp desc limit 1" >$title.md
    end
    fd -S-12b -tf -x rm
    lb mergedbs --pk id ~/d/library/datasets/social/BuonaparteII.db ~/d/library/datasets/social/reddit.db

    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/audio.db ~/lb/reddit/81_New_Music.db ~/lb/reddit/83_Classical_Composers.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/video.db ~/lb/reddit/71_Mealtime_Videos.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/tax_sounds.db ~/lb/reddit/63_Sounds.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/tax.db ~/lb/reddit/69_Taxes.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/fs/91_New_Art.db ~/lb/reddit/91_New_Art.db

    lb merge-online-local ~/lb/video.db --yes
    lb merge-online-local ~/lb/audio.db --yes

    tubeupdate
    for db in ~/lb/sites/*.db
        lb linksupdate $db
    end

    eval-shuf-repeat ~/.jobs/dl_video.sh
    eval-shuf-repeat ~/.jobs/dl_audio.sh

    ~/d/dump/image/art/
    gallery-dl --input-file (sed 's|^|https://www.instagram.com/\0|' ~/mc/91_New_Art-instagram.txt | shuf | head -15 | psub)

    ~/d/dump/image/memes/
    gallery-dl --input-file (sed 's|^|https://www.instagram.com/\0|' ~/mc/95_Memes-instagram.txt | shuf | head -15 | psub)

    ~/d/dump/porn/image/
    gallery-dl --input-file (sed 's|^|https://www.instagram.com/\0|' ~/mc/61_Photos_Unsorted-instagram.txt | shuf | head -15 | psub)

    ~/lb/
    for db in reddit/61_Photos_Unsorted.db
        lb redditupdate $db --lookback 8
    end
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/fs/61_Photos_Unsorted.db ~/lb/reddit/61_Photos_Unsorted.db

end
