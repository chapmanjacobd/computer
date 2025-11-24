# Defined interactively
function torrents.delete
    lb torrents $argv
    or return
    if confirm
        lb torrents $argv --delete-rows
    end
end
