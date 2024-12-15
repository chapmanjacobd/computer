# Defined in - @ line 2
function unlidisk_admin
    sshfs -o reconnect,IdentityFile=/home/xk/.ssh/old/admin_rsa admin@unli.xyz:/ ~/.mnt/admin
    sleep 2
    code ~/.mnt/admin/home/production/admin/public_html/
    echo fusermount -zu ~/.mnt/admin/
end
