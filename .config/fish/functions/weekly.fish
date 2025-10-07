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

    lb merge-online-local ~/lb/dl/video.db --yes
    lb merge-online-local ~/lb/dl/audio.db --yes

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
end
