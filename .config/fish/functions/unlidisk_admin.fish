# Defined in - @ line 2
function unlidisk_admin
    sshfs -o reconnect,IdentityFile=/home/xk/.ssh/admin_rsa admin@unli.xyz:/ ~/.mnt/admin
end
