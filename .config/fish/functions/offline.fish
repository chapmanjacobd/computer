function offline
    systemd-run --user --wait --pipe --collect --same-dir \
        -p NoNewPrivileges=yes -p PrivateTmp=yes \
        -p PrivateNetwork=yes -p ProtectSystem=strict \
        -p ProtectHome=read-only -- $argv
end
