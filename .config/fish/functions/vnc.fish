# Defined interactively
function vnc
    # sync_history

    #vopono -v exec --custom ./custom_openvpn.ovpn --protocol openvpn "firefox"
    if contains pakon $argv
        rdp pakon.curl-amberjack.ts.net:35589
    end
    if contains backup $argv
        # rdp backup.curl-amberjack.ts.net:35589
        /usr/NX/bin/nxplayer --session ~/.ssh/backup.nxs
    end
end
