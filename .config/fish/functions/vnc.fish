# Defined interactively
function vnc
    # sync_history

    #vopono -v exec --custom ./custom_openvpn.ovpn --protocol openvpn "firefox"
    if contains pakon $argv
        rdp
    end
    if contains backup $argv
        /usr/NX/bin/nxplayer --session ~/.ssh/backup.nxs
    end
end
