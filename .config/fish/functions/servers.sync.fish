# Defined interactively
function servers.sync
    ssh len home.clean
    print $servers | parallel server.ssh {} git pull
    print $servers | parallel server.ssh {} git -C lb/ pull
    print $servers | parallel server.ssh {} pip install --upgrade lb/
end
