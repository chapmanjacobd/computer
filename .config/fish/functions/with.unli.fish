# Defined interactively
function with.unli
    sshfs -o reconnect,sftp_server="/usr/bin/sudo /usr/libexec/openssh/sftp-server" unli.xyz:/ /net/web/
    sleep 2
    string length -q -- $argv; and $argv
    fusermount -zu /net/web/
end
