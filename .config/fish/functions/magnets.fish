# Defined interactively
function magnets
    rmdir ~/.local/Downloads/*** 2>/dev/null

    combine ~/.local/magnets not ~/.local/magnets_history | sponge ~/.local/magnets
    cat ~/.local/magnets >>~/.local/magnets_history

        pgrep tixati >/dev/null
        set tixati_is_running $status
        if not test $tixati_is_running -eq 0
            tixati &
            sleep 5
        end

        cat ~/.local/magnets | string escape | tee /dev/tty | xargs tixati
        and true >~/.local/magnets

        if not test $tixati_is_running -eq 0
            sleep 5
            pkill tixati
        end

end
