# Defined interactively
function search.firefoxhistory --wraps='lb'
    for db in (find ~/.mozilla/ -name places.sqlite)
        lb database search $db moz_places "$argv" | lb table markdown --from-json --cols url,title -p
    end
end
