function daily
    ~/
    sticky_config
    pkill -f /.ssh/control/
    rm /run/user/1000/app/org.signal.Signal/.org.chromium.Chromium.*

    lb mv ~/sync/video/keep/ /mnt/d/archive/video/keep/
    mkdir ~/sync/video/keep/

    lb christen --run ~/sync/
    files_casefold.py ~/sync/ --run

    catt volume 0 && catt volume 40
    pip install --upgrade pychromecast
    pip install --upgrade --pre yt-dlp[default]

    sync_history
    # command trash-empty 10 -f

    ~/j/social/
    library tildes ~/lb/sites/social/tildes.db xk3 --cookies ~/.local/cookies-tildes-net.txt
    for title in (sqlite --no-headers --raw-lines ~/lb/sites/social/tildes.db 'select path from media' | sed 's|.*\(/\)||' | strip | strip_quotes)
        sqlite --no-headers --raw-lines ~/lb/sites/social/tildes.db "select text from media where path like '%$title'" >$title.html
    end
    for group in (sqlite --no-headers --raw-lines ~/lb/sites/social/tildes.db 'select distinct topic_group from media')
        set group_name (string sub --start 2 -- $group)
        sqlite --no-headers --raw-lines ~/lb/sites/social/tildes.db "select path from media where topic_group = '$group' and path not like 'https://tildes.net/%' and text is null" >>$group_name.list
    end
    fd -S-12b -tf -x rm
    git add .
    preserve_titles
    git add .
    url_files_web_titles.py (url_files)
    morganize

    # library download ~/lb/dl/audio.db --audio --prefix /mnt/d/dump/audio/ -w m.time_modified=0

    lb hnadd --oldest ~/lb/hackernews/hn.db

    files_casefold.py ~/sync/ --run
    priv-daily
end
