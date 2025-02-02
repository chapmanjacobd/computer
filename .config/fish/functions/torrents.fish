# Defined interactively
function torrents
    parallel sshpc {} lb torrents $argv ::: pakon backup r730xd
end
