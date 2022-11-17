# Defined in - @ line 2
function unlidisk
    sshfs -o reconnect,IdentityFile=/home/xk/.ssh/admin_rsa admin@unli.xyz:/ ~/.mnt/web/
    code ~/.mnt/web/home/production/admin/public_html/
end
