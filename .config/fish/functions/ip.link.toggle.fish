# Defined interactively
function ip.link.toggle
    sudo ip link set dev $argv down
    sudo ip link set dev $argv up
end
