# Defined interactively
function rdpserve
    set TAILSCALE_IP (ip addr show tailscale0 | grep 'inet ' | awk '{print $2}' | cut -f1 -d'/')

    if test -z "$TAILSCALE_IP"
        set TAILSCALE_IP "127.0.0.1"
    end

    freerdp-shadow-cli -auth /port:35589 /bind-address:$TAILSCALE_IP
end
