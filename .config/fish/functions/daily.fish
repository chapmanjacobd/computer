function daily
    ~/
    sticky_config
    popline ~/.gitignore

    with_lock copy_to_pakon

    lb mv ~/sync/video/keep/ /mnt/d/archive/video/keep/
    mkdir ~/sync/video/keep/

    catt volume 0 && catt volume 40
    pip install --upgrade pychromecast
    pip install --upgrade --pre yt-dlp[default]

    sync_history
    # command trash-empty 10 -f

    ~/j/social/
    library tildes ~/d/library/datasets/social/tildes.db xk3 --cookies ~/.local/cookies-tildes-net.txt
    for title in (sqlite --no-headers --raw-lines ~/d/library/datasets/social/tildes.db 'select path from media' | sed 's|.*\(/\)||' | strip | strip_quotes)
        sqlite --no-headers --raw-lines ~/d/library/datasets/social/tildes.db "select text from media where path like '%$title'" >$title.html
    end
    fd -S-12b -tf -x rm

    library download ~/lb/audio.db --audio --prefix /mnt/d/dump/audio/ -w m.time_modified=0

    sqlite-utils rebuild-fts ~/lb/video.db media

    ~/lb/
    for db in reddit/63_Sounds.db reddit/69_Taxes.db reddit/71_Mealtime_Videos.db reddit/81_New_Music.db reddit/83_Classical_Composers.db
        lb redditupdate $db --lookback 2
    end

    lb hnadd --oldest ~/lb/hackernews/hn.db
end
