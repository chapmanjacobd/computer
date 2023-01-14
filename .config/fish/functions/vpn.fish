function vpn
    sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
    sshuttle --dns -r oci 0/0 ::/0
    or pkill tixati
end
