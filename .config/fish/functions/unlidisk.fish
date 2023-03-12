# Defined in - @ line 2
function unlidisk
    sshfs -o reconnect,IdentityFile=/home/xk/.ssh/old/admin_rsa admin@unli.xyz:/ ~/.mnt/web/
    sleep 2
    code ~/.mnt/web/home/production/admin/public_html/
    echo fusermount -zu ~/.mnt/web/
end
