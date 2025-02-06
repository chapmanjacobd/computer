# Defined interactively
function sshhfs
    mkdir -p ~/.mnt/$argv/
    sshfs -o noauto,noatime,_netdev,reconnect,ConnectTimeout=10,ServerAliveInterval=8,TCPKeepAlive=no,auto_cache,cache_timeout=1152,attr_timeout=1152,entry_timeout=1200 $argv: ~/.mnt/$argv/
end
