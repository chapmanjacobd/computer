# Defined interactively
function vnc
    if contains pakon $argv
        ssh xk@pakon -f -L 4102:localhost:4000 sleep 20 &
        sleep 2
        /usr/NX/bin/nxplayer --session ~/.ssh/ssh_pakon.nxs
    end
    if contains backup $argv
        /usr/NX/bin/nxplayer --session ~/.ssh/backup.nxs
    end
end
