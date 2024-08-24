# Defined interactively
function rdpserve
    freerdp-shadow-cli -auth /ipc-socket:/run/user/1000/rdp
end
