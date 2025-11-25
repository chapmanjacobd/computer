# Defined interactively
function search.firefoxhistory
    for db in (find ~/.mozilla/ -name places.sqlite)
        lb sdb $db moz_places "$argv" | lb tables --from-json --cols url,title -p
    end
end
