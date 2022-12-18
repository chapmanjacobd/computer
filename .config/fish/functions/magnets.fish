# Defined interactively
function magnets
    rmdir ~/d/Downloads/*** 2>/dev/null

    if test $DISPLAY = ':1001'
        pgrep tixati >/dev/null
        set tixati_is_running $status
        if not test $tixati_is_running -eq 0
            tixati &
            sleep 5
        end

        cat ~/.local/magnets | xargs tixati
        true >~/.local/magnets

        if not test $tixati_is_running -eq 0
            sleep 5
            pkill tixati
        end

    end
end
