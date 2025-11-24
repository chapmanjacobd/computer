# Defined interactively
function vpn.nl
    sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
    wg-quick up protovpn-nl
    if confirm close?
        wg-quick down protovpn-nl
    end
end
