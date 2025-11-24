# Defined via `source`
function torrents.delete.all
    torrents $argv
    or return
    if confirm
        torrents $argv --delete-rows
    end
end
