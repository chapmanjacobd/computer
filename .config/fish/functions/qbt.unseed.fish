# Defined via `source`
function qbt.unseed
    servers.qb library torrents --complete -s $argv -p
    or return
    if confirm
        servers.qb library torrents --complete --stop --move processing --delete-rows -v -s $argv -pa
    end
end
