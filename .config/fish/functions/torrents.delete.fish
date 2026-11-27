# Defined interactively
function torrents.delete --wraps='lb'
    lb torrent info $argv
    or return
    if confirm
        lb torrent info $argv --delete-rows
    end
end
