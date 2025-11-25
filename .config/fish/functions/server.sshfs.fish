# Defined interactively
function server.sshfs
    mkdir -p /net/$argv/
    sshfs -o follow_symlinks,reconnect,no_readahead,noatime,_netdev,ConnectTimeout=10,ServerAliveInterval=8,TCPKeepAlive=no,auto_cache $argv: /net/$argv/
    echo fusermount -zu /net/$argv/
end
