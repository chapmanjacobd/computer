function qbt.unseed.old
    servers.ssh qbt.unseed.old.local 2>&1 | sed '/^No media found$/d'
    set -l command_status $pipestatus[1]
    return $command_status
end
