# Defined interactively
function rdpserve
    freerdp-shadow-cli /port:35589 /bind-address:127.0.0.1 -auth
end