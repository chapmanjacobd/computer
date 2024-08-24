# Defined interactively
function rdpserve
    rm /run/user/1000/rdp
    freerdp-shadow-cli -auth /ipc-socket:/run/user/1000/rdp
end
