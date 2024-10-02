# Defined interactively
function with_unli
    sshfs -o reconnect,sftp_server="/usr/bin/sudo /usr/libexec/openssh/sftp-server" unli.xyz:/ ~/.mnt/web/
    sleep 2
    $argv
    fusermount -zu ~/.mnt/web/
end
