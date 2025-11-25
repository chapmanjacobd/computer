# Defined interactively
function sshuttle.vpn.for
    sshuttle -vr $argv[1] (dns.to.ip $argv[2..-1])
end
