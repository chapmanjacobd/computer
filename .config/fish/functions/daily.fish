function daily
    ~/
    popline ~/.gitignore
    popline ~/j/.gitignore

    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files backup:d/_tixati/ ~/d/75_Moviequeue/from_backup/
    fd '^[a-zA-Z]{3,}-[0-9]{3,5}' -x mv {} /mnt/d/69_Taxes/onejav/
    fd '[a-zA-Z]{3,5}-?[0-9]{3}' -x mv {} /mnt/d/69_Taxes/onejav/

    lb relmv /mnt/d/70_Now_Watching/Keep/* /mnt/d/77_Library/

    catt volume 0 && catt volume 40
    pip install --upgrade gallery-dl pychromecast

    ~/lb/
    for db in reddit/63_Sounds.db reddit/69_Taxes.db reddit/71_Mealtime_Videos.db reddit/81_New_Music.db reddit/83_ClassicalComposers.db
        lb redditupdate $db --lookback 2
    end

    lb hnadd --oldest ~/lb/hackernews/hn.db

    sync_history
    # command trash-empty 10 -f

    ~/j/social/
    library tildes ~/d/30_Computing/tildes.db xk3 --cookies ~/.local/cookies-tildes-net.txt
    for title in (sqlite --no-headers --raw-lines ~/d/30_Computing/tildes.db 'select path from media' | sed 's|.*\(/\)||' | strip)
        sqlite --no-headers --raw-lines ~/d/30_Computing/tildes.db "select text from media where path like '%$title'" >$title.html
    end
    fd -S-12b -tf -x rm

    lbdl ~/lb/audio.db --audio --prefix /mnt/d/81_New_Music/

    ~
    if not pgrep ffmpeg >/dev/null
        ~/d/69_Taxes_Keep/ && ffsmallpar
    end
end
