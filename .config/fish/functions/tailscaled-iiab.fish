# Defined interactively
function tailscaled-iiab
    tailscaled --tun=userspace-networking \
        --socket="$HOME/.local/iiab/tailscale/foo.sock" \
        --state="$HOME/.local/iiab/tailscale/foo.state" \
        --socks5-server=127.0.0.1:1080
end
