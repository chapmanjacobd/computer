# Defined interactively
function vpn.jp
    sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
    wg-quick up protovpn-jp
    if confirm close?
        wg-quick down protovpn-jp
    end
end
