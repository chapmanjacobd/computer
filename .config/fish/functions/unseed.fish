# Defined via `source`
function unseed
    allqb library torrents --complete -s $argv -p
    or return
    if confirm
        allqb library torrents --complete --stop --move processing --delete-rows -v -s $argv -pa
    end
end
