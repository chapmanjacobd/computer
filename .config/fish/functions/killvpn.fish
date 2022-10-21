# Defined interactively
function killvpn
    sudo sysctl -w net.ipv6.conf.all.disable_ipv6=0
    sudo pkill openvpn
end
