# Defined in - @ line 2
function unli.disk
    sshfs -o reconnect,sftp_server="/usr/bin/sudo /usr/libexec/openssh/sftp-server" unli.xyz:/ /net/web/
    sleep 2
    code /net/web/var/www/
    commandline -r "fusermount -zu /net/web/"
end
