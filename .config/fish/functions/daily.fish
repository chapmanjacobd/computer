function daily
    ~/
    popline ~/.gitignore

    rsync -auh --info=progress2 --no-inc-recursive --remove-sent-files backup:.local/Downloads/. ~/d/75_MovieQueue/from_backup/
    lb relmv /mnt/d/70_Now_Watching/Keep/* /mnt/d/77_Library/

    catt volume 0 && catt volume 40
    pip install --upgrade gallery-dl pychromecast

    ~/lb/
    for db in reddit/63_Sounds.db reddit/69_Taxes.db reddit/71_Mealtime_Videos.db reddit/81_New_Music.db reddit/83_ClassicalComposers.db
        lb redditupdate $db --lookback 2
    end

    lb hnadd --oldest ~/lb/hackernews/hn.db

    ~
    sync_history
    # command trash-empty 10 -f
    library tildes ~/d/30_Computing/tildes.db xk3 --cookies ~/.local/cookies-tildes-net.txt
    lbdl ~/lb/audio.db --audio --prefix /mnt/d/81_New_Music/

    if not pgrep ffmpeg >/dev/null
        ~/d/69_Taxes_Keep/ && ffsmallpar
    end
end
