# Defined interactively
function vpn_hk
    sudo tailscale up --advertise-exit-node=false
    sudo tailscale set --exit-node=hk

    confirm
    sudo tailscale set --exit-node=
    sudo tailscale up --advertise-exit-node
end
