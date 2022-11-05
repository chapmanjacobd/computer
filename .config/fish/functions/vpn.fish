function vpn
    sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
    fish -c 'sudo openvpn --mute-replay-warnings --script-security 2 --config /home/xk/d/30_Computing/oci.ovpn' & disown
end
