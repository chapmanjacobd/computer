# Defined interactively
function backupdl
    ~/.local/Downloads/
    sshfs -o noauto,noatime,_netdev,reconnect,ConnectTimeout=10,ServerAliveInterval=8,TCPKeepAlive=no xk@pakon:/mnt/d/ ~/.local/data/d/
    sshfs -o noauto,noatime,_netdev,reconnect,ConnectTimeout=10,ServerAliveInterval=8,TCPKeepAlive=no xk@pakon:lb/ ~/.local/data/lb/
    lb dl --image --photos lb/fs/61_Photos_Unsorted.db --prefix d/61_Photos_Unsorted/gallery-dl/
end
