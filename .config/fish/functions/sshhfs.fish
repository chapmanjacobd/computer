# Defined interactively
function sshhfs
    mkdir -p ~/.mnt/$argv/
    sshfs -o follow_symlinks,reconnect,no_readahead,noatime,_netdev,ConnectTimeout=10,ServerAliveInterval=8,TCPKeepAlive=no,auto_cache $argv: ~/.mnt/$argv/
    echo fusermount -zu ~/.mnt/$argv/
end
