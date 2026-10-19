# Defined via `source`
function qbt.unseed
    servers.qb library torrent info --complete -s $argv -p
    or return
    if confirm
        servers.qb library torrent info --complete --stop --move dump --delete-rows -v -s $argv -pa
    end
end
