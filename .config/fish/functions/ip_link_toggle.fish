# Defined interactively
function ip_link_toggle
    sudo ip link set dev $argv down
    sudo ip link set dev $argv up
end
