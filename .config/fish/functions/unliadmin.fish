# Defined in - @ line 2
function unliadmin
    sshfs -o reconnect,IdentityFile=/home/xk/.ssh/admin_rsa admin@unli.xyz:/ ~/webdev/unli
end
