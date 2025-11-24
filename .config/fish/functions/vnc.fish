# Defined interactively
function vnc
    # history.sync

    #vopono -v exec --custom ./custom_openvpn.ovpn --protocol openvpn "firefox"
    if contains pakon $argv
        /usr/NX/bin/nxplayer --session ~/.ssh/pakon.nxs
        # ssh -t pakon setsid -f 'fish -c "rdpserve"'
        # rdp pakon.curl-amberjack.ts.net:35589
    end
    if contains backup $argv
        # rdp backup.curl-amberjack.ts.net:35589
        /usr/NX/bin/nxplayer --session ~/.ssh/backup.nxs
    end
end
