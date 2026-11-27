# Defined interactively
function ip.link.toggle --wraps='sudo'
    sudo ip link set dev $argv down
    sudo ip link set dev $argv up
end
