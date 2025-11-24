# Defined interactively
function servers.ssh
    parallel -j0 server.ssh {} -- $argv ::: $servers
end
