# Defined interactively
function rdpserve
    freerdp-shadow-cli -auth /port:35589 /bind-address:127.0.0.1
end
