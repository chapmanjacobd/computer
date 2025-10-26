# Defined interactively
function torrents
    parallel sshpc {} lb torrents $argv ::: (connectable-ssh pakon backup r730xd len hk)
end
