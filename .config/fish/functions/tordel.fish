# Defined interactively
function tordel
    lb torrents $argv
    or return
    if confirm
        lb torrents $argv --delete-rows
    end
end
