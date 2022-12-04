# Defined interactively
function mount_pakond
    sshfs -o noauto,noatime,_netdev,reconnect,ConnectTimeout=10,ServerAliveInterval=8,TCPKeepAlive=no xk@pakon:/mnt/d/ /mnt/d/
end
