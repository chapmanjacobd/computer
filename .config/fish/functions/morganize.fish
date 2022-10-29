function morganize
    for f in ~/m/tabs*.txt
        sort --unique --stable --ignore-case --random-sort $f | sponge $f
    end
    for f in ~/.config/fish/functions/*.fish
        fish_indent -w $f
    end
    for f in ~/mc/*reddit.txt
        sed -e 's/\(.*\)/\L\1/' -i $f
    end

    sed -i 's|://m\.youtube|://www.youtube|' ~/mc/*

    for f in ~/mc/*.txt
        sort --unique --stable --ignore-case $f | sed '/^$/d' | sponge $f
    end

    for f in ~/mc*.cron
        sort --unique --random-sort --ignore-case $f | sed '/^$/d' | sponge $f
    end

    cat ~/mc/.jobs_71 >>~/.jobs/todo/71_Mealtime_Videos
    true >~/mc/.jobs_71

    #if test $DISPLAY = ':0'

    #  pgrep tixati >/dev/null
    #  set tixati_is_running $status
    #  if not test $tixati_is_running -eq 0
    #      tixati &
    #      sleep 5
    #  end
    #  cat ~/mc/.magnets | xargs tixati
    #  true >~/mc/.magnets
    #  if not test $tixati_is_running -eq 0
    #     sleep 5
    #      pkill tixati
    #   end

    #end

end
