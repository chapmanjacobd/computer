# Defined interactively
function torrents
    parallel sshpc {} lb-dev torrents $argv ::: pakon backup r730xd
end
