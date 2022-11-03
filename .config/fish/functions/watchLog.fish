function watchLog
    while true
        set x (logNice)
        if test -n "$x"
            notify-send Log "$x"
            sleep (math "5*60")
        end
    end
end
