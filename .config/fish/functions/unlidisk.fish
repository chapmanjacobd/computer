# Defined in - @ line 2
function unlidisk
    sshfs -o reconnect,sftp_server="/usr/bin/sudo /usr/libexec/openssh/sftp-server" unli.xyz:/ ~/.mnt/web/
    sleep 2
    code ~/.mnt/web/var/www/
    echo fusermount -zu ~/.mnt/web/
end
