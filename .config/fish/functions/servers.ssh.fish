# Defined interactively
function servers.ssh --wraps='parallel'
    parallel -j0 server.ssh {} -- $argv ::: $servers
end
