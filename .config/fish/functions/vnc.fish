# Defined interactively
function vnc
    sync_history
    if contains pakon $argv
        # ssh -fNT -R localhost:7070:localhost:22 pakon
        ssh xk@pakon -f -L 4102:localhost:4000 'sleep 20' &
        sleep 2
        /usr/NX/bin/nxplayer --session ~/.ssh/pakon.nxs
    end
    if contains backup $argv
        /usr/NX/bin/nxplayer --session ~/.ssh/backup.nxs
    end
end
