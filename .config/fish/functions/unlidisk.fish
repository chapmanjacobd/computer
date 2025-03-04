# Defined in - @ line 2
function unlidisk
    sshfs -o reconnect,sftp_server="/usr/bin/sudo /usr/libexec/openssh/sftp-server" unli.xyz:/ /net/web/
    sleep 2
    code /net/web/var/www/
    echo fusermount -zu /net/web/
end
