# Defined interactively
function vnc
    # sync_history

    #vopono -v exec --custom ./custom_openvpn.ovpn --protocol openvpn "firefox"
    if contains pakon $argv
        # ssh -fNT -R localhost:7070:localhost:22 pakon
        ssh -4 xk@pakon -L 35589:localhost:35589 'sleep 1'
        b ssh -4 xk@pakon -L 35589:localhost:35589 'sleep 20'
        sleep 1
        rdp
    end
    if contains backup $argv
        ssh -4 backup -L 4102:localhost:4000 'sleep 1'
        b ssh -4 backup -L 4102:localhost:4000 'sleep 20'
        sleep 1
        /usr/NX/bin/nxplayer --session ~/.ssh/backup.nxs
    end
end
