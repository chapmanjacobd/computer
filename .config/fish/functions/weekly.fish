function weekly
    dbackups
    trash ~/sync/.stversions/*

    update_unli_cities_visas

    mrmusic
    #mrvideo
    mrporn
    #mrrelax
    lb christen --run ~/sync/
    files_casefold.py ~/sync/ --run

    morganize

    mam_update

    for f in /home/xk/.local/share/nicotine/usershares/*
        lb nicotine-import ~/lb/sites/todo/soulseek/(path basename $f).db $f
    end

    lb-refresh
    lb-rebuild-fts

    pip install --upgrade yt-dlp gallery-dl praw library

    ~/lb/sites/social/
    reddit-user-to-sqlite user BuonaparteII
    ~/j/social/
    for title in (sqlite --no-headers --raw-lines ~/lb/sites/social/reddit.db 'select permalink from comments' | sed 's|.*\/comments\/[^\/]*\/\(.*\)/.*|\1|' | tr / '#')
        set comment_id (string split '#' -f2 $title)
        sqlite --no-headers --raw-lines ~/lb/sites/social/reddit.db "select text from comments where permalink like '%$comment_id%'" >$title.md
    end
    for title in (sqlite --no-headers --raw-lines ~/lb/sites/social/reddit.db 'select permalink from posts' | sed 's|.*\/comments\/[^\/]*\/\(.*\)/.*|\1|')
        sqlite --no-headers --raw-lines ~/lb/sites/social/reddit.db "select text from posts where permalink like '%$title%' order by timestamp desc limit 1" >$title.md
    end
    fd -S-12b -tf -x rm
    lb mergedbs --pk id ~/lb/sites/social/reddit.db ~/lb/sites/social/BuonaparteII.db

    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/reddit/81_New_Music.db ~/lb/reddit/83_Classical_Composers.db ~/lb/fs/audio.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/reddit/71_Mealtime_Videos.db ~/lb/fs/video.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/reddit/63_Sounds.db ~/lb/fs/tax_sounds.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/reddit/69_Taxes.db ~/lb/fs/tax.db
    lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/reddit/91_New_Art.db ~/lb/fs/91_New_Art.db

    lb merge-online-local ~/lb/fs/video.db --yes
    lb merge-online-local ~/lb/fs/audio.db --yes

    tubeupdate
    for db in ~/lb/sites/*.db ~/lb/sites/manual/*.db
        lb linksupdate $db
    end

    ~/d/dump/image/art/
    gallery-dl --input-file (sed 's|^|https://www.instagram.com/\0|' ~/mc/91_New_Art-instagram.txt | shuf | head -15 | psub)

    ~/d/dump/image/memes/
    gallery-dl --input-file (sed 's|^|https://www.instagram.com/\0|' ~/mc/95_Memes-instagram.txt | shuf | head -15 | psub)

    ~/d/dump/porn/image/
    gallery-dl --input-file (sed 's|^|https://www.instagram.com/\0|' ~/mc/61_Photos_Unsorted-instagram.txt | shuf | head -15 | psub)

    # timeout --preserve-status --signal INT 3d lb redditupdate --lookback 8 ~/lb/reddit/61_Photos_Unsorted.db
    # lb mergedbs --bk path --only-target-columns --ignore -t media ~/lb/fs/61_Photos_Unsorted.db ~/lb/reddit/61_Photos_Unsorted.db

    rsync -ah --info=progress2 --no-inc-recursive --partial-dir=.rsync-partial --remove-source-files hk:/home/xk/process\* hk:/var/mnt/b2/process\* hk:/var/mnt/b1/process\* /mnt/d/dump/video/
end
