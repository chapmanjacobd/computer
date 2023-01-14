function vpn
    sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1

    sudo ip route add local default dev lo table 100
    sudo ip rule add fwmark 0x01 lookup 100
    # sudo ip -6 route add local default dev lo table 100
    # sudo ip -6 rule add fwmark 0x01 lookup 100

    sudo sshuttle --dns -r oci --ssh-cmd 'ssh -F /home/xk/.ssh/config' -x 144.24.93.111 -x 192.168.0.0/16 --method tproxy --disable-ipv6 0/0 # ::/0
    or pkill tixati
end
